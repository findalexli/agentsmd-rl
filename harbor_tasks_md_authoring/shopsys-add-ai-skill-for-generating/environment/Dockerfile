FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/shopsys && \
    cd /workspace/shopsys && \
    git remote add origin https://github.com/shopsys/shopsys.git && \
    git fetch --depth=1 origin fcbde597eae4ace9547afb00f1d71e0ee2c3c036 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/shopsys
