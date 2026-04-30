FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/frontend-slides && \
    cd /workspace/frontend-slides && \
    git remote add origin https://github.com/zarazhangrui/frontend-slides.git && \
    git fetch --depth=1 origin 89a909bb09991b1b0b1e7658c7df8447dc2fa5c6 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/frontend-slides
