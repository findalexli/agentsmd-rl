FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/shokoserver && \
    cd /workspace/shokoserver && \
    git remote add origin https://github.com/ShokoAnime/ShokoServer.git && \
    git fetch --depth=1 origin 6a55c72fdaf6bf91fffeee668bd94983f1c15284 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/shokoserver
