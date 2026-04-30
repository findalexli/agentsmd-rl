FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/gotenbergbundle && \
    cd /workspace/gotenbergbundle && \
    git remote add origin https://github.com/sensiolabs/GotenbergBundle.git && \
    git fetch --depth=1 origin 937c9caa55317aef1a68d58a01b1746de2346f27 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/gotenbergbundle
