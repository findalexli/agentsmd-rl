FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/docker-tools && \
    cd /workspace/docker-tools && \
    git remote add origin https://github.com/dotnet/docker-tools.git && \
    git fetch --depth=1 origin 398b91e5a6e1eb4ac7ce803e380142eee42af252 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/docker-tools
