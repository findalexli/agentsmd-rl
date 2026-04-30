FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/video-search-and-summarization && \
    cd /workspace/video-search-and-summarization && \
    git remote add origin https://github.com/NVIDIA-AI-Blueprints/video-search-and-summarization.git && \
    git fetch --depth=1 origin 3610b04d8c27fdb31f937b23a226fc45b5c6cb1b && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/video-search-and-summarization
