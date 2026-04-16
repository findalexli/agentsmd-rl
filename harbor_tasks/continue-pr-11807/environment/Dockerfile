FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /logs/verifier

WORKDIR /workspace

# Clone the repo at base commit
RUN git clone --filter=blob:none https://github.com/continuedev/continue.git
WORKDIR /workspace/continue
RUN git checkout 3fdf35e0c1b87b5f56bfa7ec78dd915babe83ada
