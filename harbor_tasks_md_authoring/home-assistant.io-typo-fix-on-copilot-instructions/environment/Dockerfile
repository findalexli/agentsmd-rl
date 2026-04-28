FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/home-assistant.io && \
    cd /workspace/home-assistant.io && \
    git remote add origin https://github.com/home-assistant/home-assistant.io.git && \
    git fetch --depth=1 origin bcaf4624e76875279cb1d07bed7adc4b159230ea && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/home-assistant.io
