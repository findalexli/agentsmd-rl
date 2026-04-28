FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/model-server && \
    cd /workspace/model-server && \
    git remote add origin https://github.com/openvinotoolkit/model_server.git && \
    git fetch --depth=1 origin 22d1ec7777b1dfe6ba483fb3a370db788bbe69b6 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/model-server
