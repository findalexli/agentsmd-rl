FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/terraforming-mars && \
    cd /workspace/terraforming-mars && \
    git remote add origin https://github.com/terraforming-mars/terraforming-mars.git && \
    git fetch --depth=1 origin c36a74ea9600efef62a8d406465484ed893d740b && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/terraforming-mars
