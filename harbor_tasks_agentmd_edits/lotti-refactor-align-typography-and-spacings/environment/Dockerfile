FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git init /workspace/lotti && \
    cd /workspace/lotti && \
    git remote add origin https://github.com/matthiasn/lotti.git && \
    git fetch --depth=1 origin e782947f64cde48b0bd77cc38d258eee41e22b16 && \
    git checkout e782947f64cde48b0bd77cc38d258eee41e22b16 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/lotti

# No extra deps needed — test_outputs.py only reads file contents
RUN mkdir -p /logs/verifier
