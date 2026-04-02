FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates python3 python3-pip python3-venv tmux \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g tsx

RUN python3 -m pip install --break-system-packages pytest pytest-json-ctrf

# Clone repo at the pre-fix commit
RUN git init /repo \
    && cd /repo \
    && git remote add origin https://github.com/gradio-app/gradio.git \
    && git fetch --depth=1 origin e900202946a615f8fea84253d7a4377fe8a504f0 \
    && git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo
RUN git config user.email "test@test.com" && git config user.name "Test"