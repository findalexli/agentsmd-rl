FROM node:22-slim

# Install Python for test runner and git for cloning
RUN apt-get update && apt-get install -y python3 python3-pip git && rm -rf /var/lib/apt/lists/*

# Clone the repository at base commit (shallow clone for speed)
ARG BASE_COMMIT=38f0dc74f7c48e8f957995566fd427f1087541e3
RUN git clone --filter=blob:none --depth=100 https://github.com/apache/superset.git /workspace/superset && \
    cd /workspace/superset && \
    git checkout ${BASE_COMMIT}

# Set working directory to the echarts plugin
WORKDIR /workspace/superset/superset-frontend/plugins/plugin-chart-echarts

# Install plugin dependencies using the monorepo root package.json
# First install root dependencies, then link the plugin
WORKDIR /workspace/superset/superset-frontend
RUN npm ci --legacy-peer-deps || npm install --legacy-peer-deps

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory back to plugin for tests
WORKDIR /workspace/superset/superset-frontend/plugins/plugin-chart-echarts
