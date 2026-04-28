FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y     git curl ca-certificates build-essential tmux python3     && rm -rf /var/lib/apt/lists/*

# Pre-install bun so tests don't each download it
RUN npm install -g bun@1.3.11

# Clone repo at base commit (before fix)
RUN git init /workspace/opencode &&     cd /workspace/opencode &&     git remote add origin https://github.com/anomalyco/opencode.git &&     git fetch --depth=1 origin d2bfa92e7438eb7ac7c4e2d72fca708f27c52ba3 &&     git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/opencode
