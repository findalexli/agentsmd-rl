FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/wegent && \
    cd /workspace/wegent && \
    git remote add origin https://github.com/wecode-ai/Wegent.git && \
    git fetch --depth=1 origin 0de47aac7e7f91595ed98bc4f0d73eaf04cfea70 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/wegent
