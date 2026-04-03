FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Configure git
RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Agent"

# Clone gradio at the base commit (before fix)
RUN git init /workspace/gradio && \
    cd /workspace/gradio && \
    git remote add origin https://github.com/gradio-app/gradio.git && \
    git fetch --depth=1 origin 6011b00d0154b85532fa901dd73cf8fa7d86fd04 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/gradio