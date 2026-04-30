FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/wordpress-activitypub && \
    cd /workspace/wordpress-activitypub && \
    git remote add origin https://github.com/Automattic/wordpress-activitypub.git && \
    git fetch --depth=1 origin f9fdc6e02a1382457b0bfcd6491218b92128ed10 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/wordpress-activitypub
