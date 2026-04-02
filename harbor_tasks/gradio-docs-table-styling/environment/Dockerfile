FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

RUN git init /workspace/gradio \
    && cd /workspace/gradio \
    && git remote add origin https://github.com/gradio-app/gradio.git \
    && git fetch --depth 1 origin e8dadd648483b6016913a9b7fa2580dbc08cb823 \
    && git checkout FETCH_HEAD \
    && git config user.email "agent@test.com" \
    && git config user.name "Agent"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/gradio