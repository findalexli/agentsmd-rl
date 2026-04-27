FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/planning-with-files && \
    cd /workspace/planning-with-files && \
    git remote add origin https://github.com/OthmanAdi/planning-with-files.git && \
    git fetch --depth=1 origin acfd2f0c740a3bb597efdc3548c89635b96e3265 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/planning-with-files
