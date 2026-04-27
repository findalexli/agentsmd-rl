FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/awesome-cursorrules && \
    cd /workspace/awesome-cursorrules && \
    git remote add origin https://github.com/PatrickJS/awesome-cursorrules.git && \
    git fetch --depth=1 origin 867da0c98fb8498cb1b92db507acc1ccccd6a6f5 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/awesome-cursorrules
