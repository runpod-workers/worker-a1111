# Base image
FROM runpod/pytorch:3.10-2.0.0-117

# Use bash shell with pipefail option
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Set the working directory
WORKDIR /

# Set the environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/workspace/venv/bin:$PATH"
ENV PATH="${PATH}:/workspace/stable-diffusion-webui/venv/bin"

# Update and upgrade the system packages
RUN apt update && \
    apt upgrade -y && \
    apt install -y  --no-install-recommends \
    software-properties-common \
    git \
    openssh-server \
    libglib2.0-0 \
    libsm6 \
    libgl1 \
    libxrender1 \
    libxext6 \
    ffmpeg \
    wget \
    curl \
    psmisc \
    rsync \
    supervisor \
    vim \
    pkg-config \
    libcairo2-dev \
    libgoogle-perftools4 libtcmalloc-minimal4 \
    apt-transport-https ca-certificates && \
    update-ca-certificates\
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies (Worker Template)
COPY builder/requirements.txt /requirements.txt
RUN pip install --upgrade pip && \
    pip install -r /requirements.txt --no-cache-dir && \
    rm /requirements.txt

# Install the stable-diffusion-webui
RUN git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git /workspace


# Download the model
RUN wget -O model.safetensors https://civitai.com/api/download/models/15236 --content-disposition

# Add src files and execute cache.py
COPY builder/cache.py /workspace/stable-diffusion-webui/cache.py
RUN python /workspace/stable-diffusion-webui/cache.py --use-cpu=all --ckpt /model.safetensors

# Setup the API server using supervisor
RUN mkdir -p /var/log/supervisor
COPY builder/webui_api.conf /etc/supervisor/conf.d/supervisord.conf

ADD src .

# Add start.sh and make it executable
RUN chmod +x /start.sh

# Cleanup section (Worker Template)
RUN apt-get autoremove -y && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/*

CMD start.sh
