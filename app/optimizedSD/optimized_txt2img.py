import base64
import io
import time
from contextlib import nullcontext
from itertools import islice
from os.path import join
from random import randint

import numpy as np
import torch
from PIL import Image
from einops import rearrange
from ldm.util import instantiate_from_config
from omegaconf import OmegaConf
from pytorch_lightning import seed_everything
from torch import autocast
from tqdm import tqdm, trange
from transformers import logging

from optimizedSD.optimUtils import split_weighted_subprompts, logger
from optimizedSD.arguments import Arguments

CKPT_PATH = "models/ldm/stable-diffusion-v1/"
DEFAULT_CKPT = "v1-5-pruned.ckpt"

# from samplers import CompVisDenoiser
logging.set_verbosity_error()


def chunk(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


def load_model_from_config(ckpt, verbose=False):
    print(f"Loading model from {ckpt}")
    pl_sd = torch.load(ckpt, map_location="cpu")
    if "global_step" in pl_sd:
        print(f"Global Step: {pl_sd['global_step']}")
    sd = pl_sd["state_dict"]
    return sd


class StableDiffusionTxt2Img:
    def __init__(self):
        self.config = OmegaConf.load("optimizedSD/v1-inference.yaml")

    def imagine(self, opt: Arguments, image_format: str) -> list:
        image_data = []

        if opt.seed is None:
            opt.seed = randint(0, 1000000)
        seed_everything(opt.seed)

        # Logging
        logger(vars(opt), log_csv="logs/txt2img_logs.csv")

        ckpt_path = join(CKPT_PATH, opt.model or DEFAULT_CKPT)

        sd = load_model_from_config(ckpt_path)
        li, lo = [], []
        for key, value in sd.items():
            sp = key.split(".")
            if (sp[0]) == "model":
                if "input_blocks" in sp:
                    li.append(key)
                elif "middle_block" in sp:
                    li.append(key)
                elif "time_embed" in sp:
                    li.append(key)
                else:
                    lo.append(key)
        for key in li:
            sd["model1." + key[6:]] = sd.pop(key)
        for key in lo:
            sd["model2." + key[6:]] = sd.pop(key)

        model = instantiate_from_config(self.config.modelUNet)
        _, _ = model.load_state_dict(sd, strict=False)
        model.eval()
        model.unet_bs = opt.unet_bs
        model.cdevice = opt.device
        model.turbo = opt.turbo

        modelCS = instantiate_from_config(self.config.modelCondStage)
        _, _ = modelCS.load_state_dict(sd, strict=False)
        modelCS.eval()
        modelCS.cond_stage_model.device = opt.device

        modelFS = instantiate_from_config(self.config.modelFirstStage)
        _, _ = modelFS.load_state_dict(sd, strict=False)
        modelFS.eval()
        del sd

        if opt.device != "cpu" and opt.precision == "autocast":
            model.half()
            modelCS.half()

        start_code = None
        if opt.fixed_code:
            start_code = torch.randn([opt.n_samples, opt.C, opt.H // opt.f, opt.W // opt.f], device=opt.device)

        batch_size = opt.n_samples
        n_rows = opt.n_rows if opt.n_rows > 0 else batch_size
        if not opt.from_file:
            assert opt.prompt is not None
            prompt = opt.prompt
            print(f"Using prompt: {prompt}")
            data = [batch_size * [prompt]]

        else:
            print(f"reading prompts from {opt.from_file}")
            with open(opt.from_file, "r") as f:
                text = f.read()
                print(f"Using prompt: {text.strip()}")
                data = text.splitlines()
                data = batch_size * list(data)
                data = list(chunk(sorted(data), batch_size))

        if opt.precision == "autocast" and opt.device != "cpu":
            precision_scope = autocast
        else:
            precision_scope = nullcontext

        seeds = ""
        with torch.no_grad():

            all_samples = list()
            for n in trange(opt.n_iter, desc="Sampling"):
                for prompts in tqdm(data, desc="data"):

                    # sample_path = os.path.join(outpath, "_".join(re.split(":| ", prompts[0])))[:150]
                    # os.makedirs(sample_path, exist_ok=True)
                    # base_count = len(os.listdir(sample_path))

                    with precision_scope("cuda"):
                        modelCS.to(opt.device)
                        uc = None
                        if opt.scale != 1.0:
                            uc = modelCS.get_learned_conditioning(batch_size * [""])
                        if isinstance(prompts, tuple):
                            prompts = list(prompts)

                        subprompts, weights = split_weighted_subprompts(prompts[0])
                        if len(subprompts) > 1:
                            c = torch.zeros_like(uc)
                            totalWeight = sum(weights)
                            # normalize each "sub prompt" and add it
                            for i in range(len(subprompts)):
                                weight = weights[i]
                                # if not skip_normalize:
                                weight = weight / totalWeight
                                c = torch.add(c, modelCS.get_learned_conditioning(subprompts[i]), alpha=weight)
                        else:
                            c = modelCS.get_learned_conditioning(prompts)

                        shape = [opt.n_samples, opt.C, opt.H // opt.f, opt.W // opt.f]

                        if opt.device != "cpu":
                            mem = torch.cuda.memory_allocated() / 1e6
                            modelCS.to("cpu")
                            while torch.cuda.memory_allocated() / 1e6 >= mem:
                                time.sleep(1)

                        samples_ddim = model.sample(
                            S=opt.ddim_steps,
                            conditioning=c,
                            seed=opt.seed,
                            shape=shape,
                            verbose=False,
                            unconditional_guidance_scale=opt.scale,
                            unconditional_conditioning=uc,
                            eta=opt.ddim_eta,
                            x_T=start_code,
                            sampler=opt.sampler,
                        )

                        modelFS.to(opt.device)

                        print(samples_ddim.shape)
                        print("saving images")
                        for i in range(batch_size):
                            x_samples_ddim = modelFS.decode_first_stage(samples_ddim[i].unsqueeze(0))
                            x_sample = torch.clamp((x_samples_ddim + 1.0) / 2.0, min=0.0, max=1.0)
                            x_sample = 255.0 * rearrange(x_sample[0].cpu().numpy(), "c h w -> h w c")

                            if image_format == 'binary':
                                image = Image.fromarray(x_sample.astype(np.uint8))
                                img_byte_arr = io.BytesIO()
                                image.save(img_byte_arr, format=opt.format)
                                b64_data = base64.b64encode(img_byte_arr.getvalue()).decode()
                                image_data.append(b64_data)
                            else:
                                image_data.append(Image.fromarray(x_sample.astype(np.uint8)))

                            # Image.fromarray(x_sample.astype(np.uint8)).save(
                            #     os.path.join(sample_path,
                            #                  "seed_" + str(opt.seed) + "_" + f"{base_count:05}.{opt.format}")
                            # )
                            seeds += str(opt.seed) + ","
                            opt.seed += 1

                        if opt.device != "cpu":
                            mem = torch.cuda.memory_allocated() / 1e6
                            modelFS.to("cpu")
                            while torch.cuda.memory_allocated() / 1e6 >= mem:
                                time.sleep(1)
                        del samples_ddim
                        print("memory_final = ", torch.cuda.memory_allocated() / 1e6)

                        return image_data

        # toc = time.time()

        # time_taken = (toc - tic) / 60.0

        # print(
        #     (
        #             "Samples finished in {0:.2f} minutes and exported to "
        #             + sample_path
        #             + "\n Seeds used = "
        #             + seeds[:-1]
        #     ).format(time_taken)
        # )
