FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/cluster-api-provider-proxmox && \
    cd /workspace/cluster-api-provider-proxmox && \
    git remote add origin https://github.com/ionos-cloud/cluster-api-provider-proxmox.git && \
    git fetch --depth=1 origin 7597baf342eefd584b9a5fe2701c09ae66be4655 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/cluster-api-provider-proxmox
