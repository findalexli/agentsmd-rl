FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential python3 tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone gradio at the base commit (before fix)
RUN git init /workspace && \
    cd /workspace && \
    git remote add origin https://github.com/gradio-app/gradio.git && \
    git fetch --depth=1 origin 911dc366e56e9210fd260300915d408058ae18c6 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace

# Copy test files

# Install TypeScript compiler API (needed by test_outputs.py AST checks)
RUN cd /tests && npm install typescript