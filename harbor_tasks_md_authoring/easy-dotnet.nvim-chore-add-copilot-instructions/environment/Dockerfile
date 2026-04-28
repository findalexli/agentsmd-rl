FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/easy-dotnet.nvim && \
    cd /workspace/easy-dotnet.nvim && \
    git remote add origin https://github.com/GustavEikaas/easy-dotnet.nvim.git && \
    git fetch --depth=1 origin c7de3813184a69b0eeb5b41581dd49dcfe1e8587 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/easy-dotnet.nvim
