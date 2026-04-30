FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/rescript-vscode && \
    cd /workspace/rescript-vscode && \
    git remote add origin https://github.com/rescript-lang/rescript-vscode.git && \
    git fetch --depth=1 origin c1b3031f021b4a3f4c20f0fa9d70b0f1e2406a14 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/rescript-vscode
