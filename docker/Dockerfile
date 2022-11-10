FROM nvidia/cuda:11.4.1-cudnn8-devel-ubuntu20.04

# update apt sources to tsinghua
RUN sed -i s@/archive.ubuntu.com/@/mirrors.tuna.tsinghua.edu.cn/@g /etc/apt/sources.list
RUN apt-get clean

RUN echo "Asia/Shanghai" > /etc/timezone
RUN apt-get update

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata

# Install some basic utilities
RUN apt-get install -y \
    curl \
    ca-certificates \
    sudo \
    git \
    bzip2 \
    libx11-6 \
    python3 \
    python3-pip \
    libglfw3-dev \
    libgles2-mesa-dev \
    libglib2.0-0

# Create a working directory
RUN mkdir /app
WORKDIR /app

RUN cd /app
RUN git clone https://github.com/AleutianXie/stable-dreamfusion.git

# Add token
RUN echo "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" > /app/stable-dreamfusion/TOKEN

# 修改pip源为清华源
RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

RUN pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu116

WORKDIR /app/stable-dreamfusion

RUN pip3 install -r requirements.txt
RUN pip3 install git+https://github.com/NVlabs/nvdiffrast/

# Needs nvidia runtime, if you have "No CUDA runtime is found" error: https://stackoverflow.com/questions/59691207/docker-build-with-nvidia-runtime, first answer
# RUN pip3 install git+https://github.com/NVlabs/tiny-cuda-nn/#subdirectory=bindings/torch

RUN pip3 install git+https://github.com/openai/CLIP.git
# RUN bash scripts/install_ext.sh


RUN python3 /app/stable-dreamfusion/main.py --text "a hamburger" --workspace k8s -O --iters 4800 --save_mesh

# 临时解次打docker包后代码有更情况(不清缓存的时候)
RUN git pull
# python model
RUN pip install PyMySQL
RUN pip install PyMySQL[rsa]
RUN pip install pydantic
RUN pip install pydantic[dotenv]
# install oss python sdk
RUN pip install oss2

# copy resource
COPY ape/.env_prod /app/stable-dreamfusion/ape/.env_prod
COPY ape/.env_test /app/stable-dreamfusion/ape/.env_test
COPY ape/.env_dev /app/stable-dreamfusion/ape/.env_dev

# Set the default command to python3
#CMD ["python3"]

