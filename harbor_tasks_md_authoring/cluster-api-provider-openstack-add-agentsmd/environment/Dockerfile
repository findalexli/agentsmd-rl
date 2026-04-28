FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/cluster-api-provider-openstack && \
    cd /workspace/cluster-api-provider-openstack && \
    git remote add origin https://github.com/kubernetes-sigs/cluster-api-provider-openstack.git && \
    git fetch --depth=1 origin a8f065b796d4b2dcd7a85108fdef1c3e50e5f7f8 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/cluster-api-provider-openstack
