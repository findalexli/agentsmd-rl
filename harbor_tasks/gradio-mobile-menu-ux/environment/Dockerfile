FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before the fix)
RUN git init /workspace && \
    cd /workspace && \
    git remote add origin https://github.com/gradio-app/gradio.git && \
    git fetch --depth=1 origin 7760161258abe6329b754dd6d2511fc3b61fed95 && \
    git checkout FETCH_HEAD

# Install svelte compiler + prettier for syntax validation and formatting checks
# (in separate dir to avoid workspace: protocol issues)
RUN mkdir /svelte-tools && cd /svelte-tools && npm init -y && \
    npm install svelte@4 prettier prettier-plugin-svelte
ENV NODE_PATH=/svelte-tools/node_modules

# Configure git user for agent commits
RUN cd /workspace && \
    git config user.email "agent@test.com" && \
    git config user.name "Agent"

RUN mkdir -p /logs/verifier

WORKDIR /workspace