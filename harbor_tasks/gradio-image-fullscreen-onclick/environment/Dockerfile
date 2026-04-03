FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential python3 python3-pip tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone gradio at the base commit (before the fix)
RUN git init /workspace && \
    cd /workspace && \
    git remote add origin https://github.com/gradio-app/gradio.git && \
    git fetch --depth=1 origin 4a4c7f3b0d6fd8009fdafc580d5852984f961db1 && \
    git checkout FETCH_HEAD

# Install prettier + svelte plugin for formatting checks
RUN npm install -g prettier prettier-plugin-svelte

# Configure git
RUN cd /workspace && \
    git config user.email "agent@test.com" && \
    git config user.name "Agent"

RUN mkdir -p /logs/verifier

WORKDIR /workspace