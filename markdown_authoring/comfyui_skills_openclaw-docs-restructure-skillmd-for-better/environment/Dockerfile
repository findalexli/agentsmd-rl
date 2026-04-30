FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/comfyui-skills-openclaw && \
    cd /workspace/comfyui-skills-openclaw && \
    git remote add origin https://github.com/HuangYuChuh/ComfyUI_Skills_OpenClaw.git && \
    git fetch --depth=1 origin 86472b2744fff194e5364955d6a5fbaa5c39e7bb && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/comfyui-skills-openclaw
