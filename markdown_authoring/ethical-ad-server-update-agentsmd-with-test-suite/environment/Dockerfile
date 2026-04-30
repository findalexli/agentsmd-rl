FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/ethical-ad-server && \
    cd /workspace/ethical-ad-server && \
    git remote add origin https://github.com/readthedocs/ethical-ad-server.git && \
    git fetch --depth=1 origin bc43ee7a426cd777166d4700035a5b0c57cb0856 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ethical-ad-server
