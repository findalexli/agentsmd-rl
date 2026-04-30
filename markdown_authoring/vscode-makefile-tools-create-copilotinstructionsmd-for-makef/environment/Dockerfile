FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/vscode-makefile-tools && \
    cd /workspace/vscode-makefile-tools && \
    git remote add origin https://github.com/microsoft/vscode-makefile-tools.git && \
    git fetch --depth=1 origin 55ca34a75cabdcf87f7f41c9b96daeb94337e076 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/vscode-makefile-tools
