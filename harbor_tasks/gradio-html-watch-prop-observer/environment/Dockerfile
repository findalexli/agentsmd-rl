FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace /logs/verifier

WORKDIR /workspace

RUN git init /workspace/gradio && \
    cd /workspace/gradio && \
    git remote add origin https://github.com/gradio-app/gradio.git && \
    git fetch --depth=1 origin f4c3a6dcb45218722d3150baef953c731d3eccf2 && \
    git checkout FETCH_HEAD

RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Test Agent"

WORKDIR /workspace/gradio