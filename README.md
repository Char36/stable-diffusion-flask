# Run guide

## Prerequisites
- `Python` >= 3.8
- `Conda` (latest)
- [stable diffusion model](#stable-diffusion-model) 

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

## Example requests:

### Stream single image
``` http request
POST /imagine HTTP/1.1
Host: 127.0.0.1:5000
Accept: image/png
Content-Type: application/json
Content-Length: 262

{
   "prompt": "lord of the rings battle scene, highly detailed realistic middle earth, ents orcs knights fighting in battle siege game of thrones rob stark, HDR lighting, birds-eye view",
   "H": 960,
   "W": 1280,
   "ddim_steps": 50,
   "n_samples": 1
}
```

### Multiple images, JSON serialized response

Returns _n_ images as a JSON array of B64-encoded byte arrays, 
where _n_ :== _n_samples_ * _n_iter_.

The below example generates 10 images

``` http request
POST /imagine HTTP/1.1
Host: 127.0.0.1:5000
Accept: application.json
Content-Type: application/json
Content-Length: 279

{
   "prompt": "lord of the rings battle scene, highly detailed realistic middle earth, ents orcs knights fighting in battle siege game of thrones rob stark, HDR lighting, birds-eye view",
   "H": 960,
   "W": 1280,
   "ddim_steps": 50,
   "n_samples": 2,
   "n_iter": 5
}
```

### Development
- The main HTTP API controller (Flask) is in `app\main.py`.
- All of the application core functionality is inside of the `app\optimizedSD` folder.

The two entry-points to the application core are in:
- `optimizedSD\optimized_txt2img.py`
- `optimizedSD\optimized_img2img.py`