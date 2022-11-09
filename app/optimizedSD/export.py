import importlib
from os.path import join

import torch
from omegaconf import OmegaConf
from torch.autograd import Variable

CKPT_PATH = "../models/ldm/stable-diffusion-v1/"
DEFAULT_CKPT = "v1-5-pruned.ckpt"

config = OmegaConf.load("v1-inference.yaml")


def get_obj_from_str(string, reload=False):
    module, cls = string.rsplit(".", 1)
    if reload:
        module_imp = importlib.import_module(module)
        importlib.reload(module_imp)
    return getattr(importlib.import_module(module, package=None), cls)


def load_model_from_config(ckpt, verbose=False):
    print(f"Loading model from {ckpt}")
    pl_sd = torch.load(ckpt, map_location="cpu")
    if "global_step" in pl_sd:
        print(f"Global Step: {pl_sd['global_step']}")
    sd = pl_sd["state_dict"]
    return sd


def instantiate_from_config(conf):
    if "target" not in conf:
        if conf == '__is_first_stage__':
            return None
        elif conf == "__is_unconditional__":
            return None
        raise KeyError("Expected key `target` to instantiate.")
    return get_obj_from_str(conf["target"])(**conf.get("params", dict()))


def export(path=DEFAULT_CKPT):
    # Logging
    ckpt_path = join(CKPT_PATH, path)

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

    model = instantiate_from_config(config.modelUNet)
    model.load_state_dict(sd, strict=False)

    # dummy_data = torch.randn([1, 4, 960 // 8, 1280 // 8], device="cuda")
    dummy_input = Variable(torch.randn([1, 4, 960 // 8, 1280 // 8])).cuda()

    torch.onnx.export(model, dummy_input, 'model.onnx', verbose=False);


def main():
    export()


if __name__ == "__main__":
    main()
