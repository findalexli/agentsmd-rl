FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/anolisa && \
    cd /workspace/anolisa && \
    git remote add origin https://github.com/alibaba/anolisa.git && \
    git fetch --depth=1 origin d7dd7e6cbddd6ce869173c9703ffac3da3c51c74 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/anolisa
