FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/fmd-framework && \
    cd /workspace/fmd-framework && \
    git remote add origin https://github.com/edkreuk/FMD_FRAMEWORK.git && \
    git fetch --depth=1 origin 92fd693fad60b45c6b2adcc66f80958229e2dc98 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/fmd-framework
