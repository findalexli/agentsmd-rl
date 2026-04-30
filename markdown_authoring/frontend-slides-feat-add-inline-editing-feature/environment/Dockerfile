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
    git fetch --depth=1 origin 448cec22c8fca4131b8d4591f16dfdab7382c43f && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/frontend-slides
