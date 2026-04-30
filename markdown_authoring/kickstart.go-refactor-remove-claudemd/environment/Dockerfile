FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/kickstart.go && \
    cd /workspace/kickstart.go && \
    git remote add origin https://github.com/raeperd/kickstart.go.git && \
    git fetch --depth=1 origin 5f56130b13bfcfdb68a285b983d3d32002e560f2 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/kickstart.go
