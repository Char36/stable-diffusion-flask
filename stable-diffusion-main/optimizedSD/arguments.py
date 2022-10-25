import dataclasses
import json
from dataclasses import dataclass


@dataclass
class Arguments:
    prompt: str
    from_file: bool = False
    outdir: str = "outputs/txt2img-samples"
    ddim_steps: int = 50
    ddim_eta: float = 0.0
    n_iter: int = 1
    H: int = 512
    W: int = 512
    C: int = 4
    f: int = 8
    n_samples: int = 1
    n_rows: int = 0
    add_argument: float = 10
    device: str = "cuda"
    seed: int = None
    unet_bs: int = 1
    turbo: bool = True
    precision: str = "autocast"
    format: str = "png"
    sampler: str = "plms"
    scale: int = 7.5
    fixed_code: bool = True

    def __init__(self):
        pass

    """ model bind """

    def bind_json(self, raw):
        dumps = json.loads(raw)
        for field in dataclasses.fields(self):
            try:
                value = dumps[field.name]
                setattr(self, field.name, value)
            except:
                pass
