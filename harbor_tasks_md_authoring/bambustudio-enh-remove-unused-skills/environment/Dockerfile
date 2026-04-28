FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/bambustudio && \
    cd /workspace/bambustudio && \
    git remote add origin https://github.com/bambulab/BambuStudio.git && \
    git fetch --depth=1 origin bf68eece13cbc05a9f9eaf3e1761a4d020ccd411 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/bambustudio
