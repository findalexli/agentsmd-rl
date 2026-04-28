FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/homebrew-dotnet-sdk-versions && \
    cd /workspace/homebrew-dotnet-sdk-versions && \
    git remote add origin https://github.com/isen-ng/homebrew-dotnet-sdk-versions.git && \
    git fetch --depth=1 origin 59efab5c43d1fc6672dc5a36cc2031ee448a69b1 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/homebrew-dotnet-sdk-versions
