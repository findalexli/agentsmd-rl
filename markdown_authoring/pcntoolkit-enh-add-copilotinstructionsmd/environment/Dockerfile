FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/pcntoolkit && \
    cd /workspace/pcntoolkit && \
    git remote add origin https://github.com/predictive-clinical-neuroscience/PCNtoolkit.git && \
    git fetch --depth=1 origin e09154b32b8d039c516946bcb6ff6bd55bf5158b && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/pcntoolkit
