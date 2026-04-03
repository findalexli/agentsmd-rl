FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential python3 tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone gradio at the base commit (before the fix)
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/gradio-app/gradio.git && \
    git fetch --depth=1 origin dcfc429a8125204c3aafeabcab251dd7580f9a60 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo