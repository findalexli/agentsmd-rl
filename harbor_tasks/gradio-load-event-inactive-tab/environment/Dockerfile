FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Configure git
RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Agent"

# Clone gradio at the base commit (before fix)
RUN git clone https://github.com/gradio-app/gradio.git /workspace/gradio && \
    cd /workspace/gradio && \
    git checkout 6011b00d0154b85532fa901dd73cf8fa7d86fd04

RUN mkdir -p /logs/verifier

WORKDIR /workspace/gradio