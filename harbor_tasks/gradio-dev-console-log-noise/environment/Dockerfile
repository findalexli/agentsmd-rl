FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential python3 tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone gradio at the base commit (before fix)
RUN git init /workspace && \
    cd /workspace && \
    git remote add origin https://github.com/gradio-app/gradio.git && \
    git fetch --depth=1 origin 424a4e4bcfeace96f7f5a678b56a578ad2002cf4 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace

# Copy test files