FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git init /workspace/react && \
    cd /workspace/react && \
    git remote add origin https://github.com/facebook/react.git && \
    git fetch --depth=1 origin 74568e8627aa43469b74f2972f427a209639d0b6 && \
    git checkout FETCH_HEAD \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/react

# Install json5 for parseConfigOverrides tests
RUN npm install --no-save --no-package-lock json5@2 2>/dev/null || \
    (mkdir -p node_modules/json5 && \
     cd /tmp && npm pack json5@2.2.3 && \
     tar xf json5-2.2.3.tgz && \
     cp -r package/* /workspace/react/node_modules/json5/)

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
