FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/android-image-cropper && \
    cd /workspace/android-image-cropper && \
    git remote add origin https://github.com/CanHub/Android-Image-Cropper.git && \
    git fetch --depth=1 origin 4833a5d83b78b5498b68228188d83b1e8611ae70 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/android-image-cropper
