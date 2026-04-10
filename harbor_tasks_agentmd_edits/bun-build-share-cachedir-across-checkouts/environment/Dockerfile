FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Install Node.js 24.x for TypeScript support
RUN curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    rm -rf /var/lib/apt/lists/*

# Clone bun at the base commit (before the fix)
RUN git init /workspace/bun && \
    cd /workspace/bun && \
    git remote add origin https://github.com/oven-sh/bun.git && \
    git fetch --depth=1 origin 485ec522a22b469b336aece8276b507a71665a87 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

# Install TypeScript globally for type checking
RUN npm install -g typescript@5.4.5

# Install bun types for type checking - use specific version with globSync support
RUN npm install -g @types/bun@1.2.22

# Link the types so tsc can find them
RUN mkdir -p /workspace/bun/node_modules/@types && \
    ln -s /usr/lib/node_modules/@types/bun /workspace/bun/node_modules/@types/bun && \
    ln -s /usr/lib/node_modules/@types/bun/node_modules/bun-types /workspace/bun/node_modules/bun-types

RUN mkdir -p /logs/verifier

WORKDIR /workspace/bun
