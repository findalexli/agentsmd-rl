FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/youre-the-os && \
    cd /workspace/youre-the-os && \
    git remote add origin https://github.com/plbrault/youre-the-os.git && \
    git fetch --depth=1 origin b3e4c707e5c8b7b36e1cf98ebac5539d910017e1 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/youre-the-os
