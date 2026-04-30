FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/backpack && \
    cd /workspace/backpack && \
    git remote add origin https://github.com/Skyscanner/backpack.git && \
    git fetch --depth=1 origin 48f622bf0e1ed987b0b49b4782a3081818645cd6 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/backpack
