FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/jsbeeb && \
    cd /workspace/jsbeeb && \
    git remote add origin https://github.com/mattgodbolt/jsbeeb.git && \
    git fetch --depth=1 origin 18153c5a957595cc02e6185a83d8566c8c0ed6c8 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/jsbeeb
