FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/goose-skills && \
    cd /workspace/goose-skills && \
    git remote add origin https://github.com/gooseworks-ai/goose-skills.git && \
    git fetch --depth=1 origin 7778da73aaa81847ba7bf26d61e549b3d8ac4a5b && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/goose-skills
