FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/ai-for-beginners && \
    cd /workspace/ai-for-beginners && \
    git remote add origin https://github.com/microsoft/AI-For-Beginners.git && \
    git fetch --depth=1 origin 7a0cac4cf1d73f9f85e292b4f6afd0f486056cfb && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ai-for-beginners
