FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/vscode-mssql && \
    cd /workspace/vscode-mssql && \
    git remote add origin https://github.com/microsoft/vscode-mssql.git && \
    git fetch --depth=1 origin 6936ef864daf44367ebd4f4a79c731b887f552cb && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/vscode-mssql
