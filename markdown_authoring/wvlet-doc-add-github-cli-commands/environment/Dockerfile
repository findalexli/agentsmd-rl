FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/wvlet && \
    cd /workspace/wvlet && \
    git remote add origin https://github.com/wvlet/wvlet.git && \
    git fetch --depth=1 origin de5f9ea4fb76ffdb4d573f448b69884b8714b576 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/wvlet
