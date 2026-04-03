FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace /logs/verifier

# Install einops for behavioral testing
RUN pip install --no-cache-dir einops==0.8.2

WORKDIR /workspace

RUN git init /workspace/pytorch && \
    cd /workspace/pytorch && \
    git remote add origin https://github.com/pytorch/pytorch.git && \
    git fetch --depth=1 origin 98e35020c7423c304778a7044f6baa3c8a98ba6d && \
    git checkout FETCH_HEAD

ENV PYTHONPATH="/workspace/pytorch"

RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Test Agent"

WORKDIR /workspace/pytorch