FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/dpdata && \
    cd /workspace/dpdata && \
    git remote add origin https://github.com/deepmodeling/dpdata.git && \
    git fetch --depth=1 origin a89a7a47328d468a7ffe3d4c70db4675eec98563 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/dpdata
