FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/vscode-csharp && \
    cd /workspace/vscode-csharp && \
    git remote add origin https://github.com/dotnet/vscode-csharp.git && \
    git fetch --depth=1 origin f05060119a9c236cf8e315cf3434e7be20df0e54 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/vscode-csharp
