FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

RUN git clone --filter=blob:none https://github.com/matthiasn/lotti.git /workspace/lotti && \
    cd /workspace/lotti && \
    git checkout be8bbfc8f59d502773f05d99b835f122c22b18c1 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/lotti

RUN mkdir -p /logs/verifier
