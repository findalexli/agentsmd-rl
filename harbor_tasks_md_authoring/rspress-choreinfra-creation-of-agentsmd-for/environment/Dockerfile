FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/rspress && \
    cd /workspace/rspress && \
    git remote add origin https://github.com/web-infra-dev/rspress.git && \
    git fetch --depth=1 origin b9d7a5ec06020d05c22e5162c6523ec9fc1bc02b && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/rspress
