#!/bin/bash

# Start the init system
python -m /stable-diffusion-webui/webui.py --skip-python-version-check --skip-torch-cuda-test --no-tests --skip-install --ckpt /model.safetensors --lowram --xformers --force-enable-xformers --xformers-flash-attention --listen --disable-safe-unpickle --port 3000 --api --nowebui --skip-version-check  --no-hashing --no-download-sd-model &

python -u /rp_handler.py
