FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/review-gate && \
    cd /workspace/review-gate && \
    git remote add origin https://github.com/LakshmanTurlapati/Review-Gate.git && \
    git fetch --depth=1 origin f1211d956974394b661e1cd2013da1a7db5867f7 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/review-gate
