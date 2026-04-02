FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Clone gradio at the base commit (before the fix)
RUN git clone https://github.com/gradio-app/gradio.git /repo && \
    cd /repo && \
    git checkout 01352c78e560c3a6de728a4aec07027e96c27acc

# Configure git user for applying patches
RUN cd /repo && \
    git config user.email "test@test.com" && \
    git config user.name "Test"

RUN mkdir -p /logs/verifier

WORKDIR /repo