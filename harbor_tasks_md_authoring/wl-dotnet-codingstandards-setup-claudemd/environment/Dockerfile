FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/wl-dotnet-codingstandards && \
    cd /workspace/wl-dotnet-codingstandards && \
    git remote add origin https://github.com/workleap/wl-dotnet-codingstandards.git && \
    git fetch --depth=1 origin 35163af14919b3e849df2971dc69cb993e00417f && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/wl-dotnet-codingstandards
