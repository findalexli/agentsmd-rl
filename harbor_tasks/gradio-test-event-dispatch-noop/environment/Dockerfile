FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/gradio-app/gradio.git /workspace/gradio \
    && cd /workspace/gradio \
    && git checkout 6f8a0533ad0247e709fefe406961b864473d344d

RUN mkdir -p /logs/verifier

WORKDIR /workspace/gradio

# Configure git for patching
RUN git config user.email "test@test.com" && git config user.name "Test"