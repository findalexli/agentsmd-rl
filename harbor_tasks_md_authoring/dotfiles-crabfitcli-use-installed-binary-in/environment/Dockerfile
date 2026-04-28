FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/dotfiles && \
    cd /workspace/dotfiles && \
    git remote add origin https://github.com/Mic92/dotfiles.git && \
    git fetch --depth=1 origin 95bca3d8e4de3943e78cb17ead200b9b664e4715 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/dotfiles
