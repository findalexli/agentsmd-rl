FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/secure-custom-fields && \
    cd /workspace/secure-custom-fields && \
    git remote add origin https://github.com/WordPress/secure-custom-fields.git && \
    git fetch --depth=1 origin 6cf486170efe255189ce74e24be6461ff9b97665 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/secure-custom-fields
