FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/gatekeeper-library && \
    cd /workspace/gatekeeper-library && \
    git remote add origin https://github.com/open-policy-agent/gatekeeper-library.git && \
    git fetch --depth=1 origin b33dbbc579b5ae08c5a13d5d4686756670960c90 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/gatekeeper-library
