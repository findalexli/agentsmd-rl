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
    git fetch --depth=1 origin e76a1dc9dae3e3c5519a33fdfcd7d847d5a9ea60 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/dd-trace-dotnet
