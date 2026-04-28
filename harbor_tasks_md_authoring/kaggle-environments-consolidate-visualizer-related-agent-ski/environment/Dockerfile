FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/kaggle-environments && \
    cd /workspace/kaggle-environments && \
    git remote add origin https://github.com/Kaggle/kaggle-environments.git && \
    git fetch --depth=1 origin 40d16efe938eb1c0c7beaea0eb6e98fb32866c88 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/kaggle-environments
