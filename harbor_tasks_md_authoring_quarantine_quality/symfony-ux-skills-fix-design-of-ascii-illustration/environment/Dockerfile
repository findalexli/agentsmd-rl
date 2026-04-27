FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/symfony-ux-skills && \
    cd /workspace/symfony-ux-skills && \
    git remote add origin https://github.com/smnandre/symfony-ux-skills.git && \
    git fetch --depth=1 origin 69acf002af0ba461d641d8cba3f8b396016a3a79 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/symfony-ux-skills
