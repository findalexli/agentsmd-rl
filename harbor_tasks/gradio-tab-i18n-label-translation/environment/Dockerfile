FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential python3 tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone gradio at the base commit (before the fix)
RUN git clone https://github.com/gradio-app/gradio.git /repo \
    && cd /repo \
    && git checkout d720b25b575fb9817311212e1c0afa82abf27468

# Configure git user for any commits the agent may make
RUN cd /repo && git config user.email "agent@test.com" && git config user.name "Agent"

RUN mkdir -p /logs/verifier

WORKDIR /repo