FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/cc-wf-studio && \
    cd /workspace/cc-wf-studio && \
    git remote add origin https://github.com/breaking-brake/cc-wf-studio.git && \
    git fetch --depth=1 origin 852407480044960f4c95743e05d646c5487fe6a7 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/cc-wf-studio
