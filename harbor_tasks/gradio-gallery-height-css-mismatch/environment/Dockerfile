FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
      git curl ca-certificates build-essential python3 python3-pip tmux && \
    rm -rf /var/lib/apt/lists/*

ARG REPO=gradio-app/gradio
ARG COMMIT=611d40b529b6c97e41e09ae0a60804ad71a9bf58

RUN git clone --filter=blob:none https://github.com/${REPO}.git /workspace/gradio && \
    cd /workspace/gradio && \
    git checkout ${COMMIT} && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

RUN pip3 install --break-system-packages -q pytest pytest-json-ctrf

RUN mkdir -p /logs/verifier

WORKDIR /workspace/gradio