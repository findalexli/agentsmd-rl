FROM node:22-slim

# Install necessary packages
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Configure git
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# Set working directory
WORKDIR /workspace/react

# Clone React repo at the base commit (pre-fix)
ARG BASE_COMMIT=272441a9ade6bf84de11ba73039eb4c80668fa6a
RUN git init && \
    git remote add origin https://github.com/facebook/react.git && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Install dependencies (minimal for testing)
RUN yarn install --frozen-lockfile

# Sanitize snapshot - remove .git history but keep files
RUN rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

# Create logs directory
RUN mkdir -p /logs/verifier

# Set environment
ENV NODE_ENV=development
ENV CI=true
