FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/dotnet-monitor && \
    cd /workspace/dotnet-monitor && \
    git remote add origin https://github.com/dotnet/dotnet-monitor.git && \
    git fetch --depth=1 origin 9ffabc0fb4513db277236a8050103104e4a7e460 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/dotnet-monitor
