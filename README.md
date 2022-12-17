# Build and deployment information
Latest build<br>![Latest build](https://dev.azure.com/adeane999/Stable%20Diffusion/_apis/build/status/Char36.stable-diffusion-flask?branchName=deploy)

Latest release<br>![Latest release](https://vsrm.dev.azure.com/adeane999/_apis/public/Release/badge/4ef0a447-8705-4fb3-ac34-c98e0499e435/1/1) 

# Run guide

## Prerequisites
- `Python` >= 3.8
- [conda](https://docs.conda.io/en/latest/miniconda.html) (latest)
- [stable diffusion model](#stable-diffusion-model)
- A GRPC client such as [BloomRPC](https://github.com/bloomrpc/bloomrpc/releases)
- Git CLI

## Quickstart
### Stable-diffusion-model
1. Go to [huggingface/stable-diffusion-v-1-4-original](https://huggingface.co/CompVis/stable-diffusion-v-1-4-original/tree/main)
2. Create or login to an existing account to access the repository
3. Download the 4GB `.cpkt` file
4. Create a new directory `app\models\ldm\stable-diffusion-v1`
5. Place the `.cpkt` file in this directory
6. Rename the file to `model.cpkt`

### Running the API
```shell
cd .\app\
conda env create -f environment.yaml
conda activate ldm2
python main.py
```

You should see some run output like:

```console
server started
```

## Example GRPC requests:

### Common parameters
for reproducibility, you can set an image `seed`, e.g:

`"seed": 892494128`

If no seed is sent, the app will generate a pseudorandom one


### Generate multiple images

#### Request

`localhost:50051` _Unary Call_
```json
{
  "data": {
    "prompt": "[[Adolf Hitler]] on the moon, hyperrealistic, photorealistic HD, wallpaper",
    "ddim_steps": 10,
    "n_iter": 10,
    "H": 256,
    "W": 256,
    "C": 4,
    "f": 8,
    "n_samples": 1,
    "n_rows": 10,
    "seed": 424242,
    "turbo": true,
    "scale": 7.5
  }
}
```

#### Response

The image data will be in array buffer format - a serialized byte array

```json
{
  "image_data": [
    {
      "seed": "424242",
      "chunk_data": {
        "type": "Buffer",
        "data": [
          105,
          86,
          66,
          ...
        ]
      }
    }
  ]
}
```

### Development
- The GRPC API controller is in [app/main.py](app/main.py)
   - Proto files can be found in [app/protos](app/protos)
- All of the application core functionality is inside of the `app\optimizedSD` folder.

The two entry-points to the application core are in:
- `optimizedSD\optimized_txt2img.py`
- `optimizedSD\optimized_img2img.py`
