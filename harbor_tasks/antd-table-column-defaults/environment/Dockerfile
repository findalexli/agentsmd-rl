FROM node:22-slim

# Install Python for pytest runner
RUN apt-get update && apt-get install -y python3 python3-pip git && rm -rf /var/lib/apt/lists/*

# Clone ant-design at base commit
WORKDIR /workspace
ARG BASE_COMMIT=b73b49c02f70e54ffc67c6e7ec895ec8d62378f3
RUN git init /workspace/ant-design && \
    cd /workspace/ant-design && \
    git remote add origin https://github.com/ant-design/ant-design.git && \
    git fetch --depth=1 origin b73b49c02f70e54ffc67c6e7ec895ec8d62378f3 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/ant-design

# Install dependencies (skip puppeteer, playwright)
ENV PUPPETEER_SKIP_DOWNLOAD=true
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=true
RUN npm install --legacy-peer-deps || npm install --force

# Create logs directory
RUN mkdir -p /logs/verifier

# Default workdir for task
WORKDIR /workspace/ant-design
