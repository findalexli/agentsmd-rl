# Fix useDeferredValue getting stuck
FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

ARG BASE_COMMIT=ed69815cebae33b0326cc69faa90f813bb924f3b

# Clone React at pre-fix commit
RUN git clone --depth=100 --no-single-branch https://github.com/facebook/react.git react

WORKDIR /workspace/react
RUN git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT} && \
    git clean -fdx

# Sanitize: remove git history so agent can't find fix via git log
RUN rm -rf .git && \
    git init && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent" && \
    git add -A && \
    git commit -m "snapshot"

# Install dependencies (React uses yarn workspaces)
RUN corepack enable && yarn install 2>&1 | tail -30 || true

ENV NODE_ENV=development
RUN mkdir -p /logs/verifier
