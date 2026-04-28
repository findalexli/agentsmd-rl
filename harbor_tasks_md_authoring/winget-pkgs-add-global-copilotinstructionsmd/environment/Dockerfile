FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/winget-pkgs && \
    cd /workspace/winget-pkgs && \
    git remote add origin https://github.com/microsoft/winget-pkgs.git && \
    git fetch --depth=1 origin bdffec0554e2646facf702cf62d880d6a3a88f09 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/winget-pkgs
