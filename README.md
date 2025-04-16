<h1>Automatic1111 Stable Diffusion web UI</h1>

[![RunPod](https://api.runpod.io/badge/runpod-workers/worker-a1111)](https://www.runpod.io/console/hub/runpod-workers/worker-a1111)

- Runs [Automatic1111 Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui) and exposes its `txt2img` API endpoint
- Comes pre-packaged with the [**Deliberate v6**](https://huggingface.co/XpucT/Deliberate) model

---

## Usage

The `input` object accepts any valid parameter for the Automatic1111 `/sdapi/v1/txt2img` endpoint. Refer to the [Automatic1111 API Documentation](https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/API) for a full list of available parameters (like `seed`, `sampler_name`, `batch_size`, `styles`, `override_settings`, etc.).

### Example Request

Here's an example payload to generate an image:

```json
{
  "input": {
    "prompt": "a photograph of an astronaut riding a horse",
    "negative_prompt": "text, watermark, blurry, low quality",
    "steps": 25,
    "cfg_scale": 7,
    "width": 512,
    "height": 512,
    "sampler_name": "DPM++ 2M Karras"
  }
}
```
