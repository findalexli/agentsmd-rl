FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/bsl-language-server && \
    cd /workspace/bsl-language-server && \
    git remote add origin https://github.com/1c-syntax/bsl-language-server.git && \
    git fetch --depth=1 origin 04c2a674edd47197f611c2f221d878c8825f8db4 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/bsl-language-server
