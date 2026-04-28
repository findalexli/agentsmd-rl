FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/generative-ai-for-beginners && \
    cd /workspace/generative-ai-for-beginners && \
    git remote add origin https://github.com/microsoft/generative-ai-for-beginners.git && \
    git fetch --depth=1 origin b57c7aa7661a35572cfa26efc9e701a10a6d2305 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/generative-ai-for-beginners
