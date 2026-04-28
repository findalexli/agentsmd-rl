FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/fabric-cicd && \
    cd /workspace/fabric-cicd && \
    git remote add origin https://github.com/microsoft/fabric-cicd.git && \
    git fetch --depth=1 origin ef3e813d1f2f05fb791948f48ed17a07e17953ee && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/fabric-cicd
