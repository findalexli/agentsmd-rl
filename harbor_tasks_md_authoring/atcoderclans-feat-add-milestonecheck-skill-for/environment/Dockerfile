FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/atcoderclans && \
    cd /workspace/atcoderclans && \
    git remote add origin https://github.com/KATO-Hiro/AtCoderClans.git && \
    git fetch --depth=1 origin da6b25afcfcaf05f7f81cf6259762fe51e973b09 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/atcoderclans
