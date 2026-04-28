FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/dd-trace-dotnet && \
    cd /workspace/dd-trace-dotnet && \
    git remote add origin https://github.com/DataDog/dd-trace-dotnet.git && \
    git fetch --depth=1 origin 6ca218c2c03c8aaedce0c1dc4d07cf9ed6062b54 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/dd-trace-dotnet
