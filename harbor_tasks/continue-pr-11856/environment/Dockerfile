FROM node:22-slim

# Install python3 and pytest for test runner
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && pip3 install --no-cache-dir --break-system-packages pytest \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone the repository at the base commit
RUN git clone --filter=blob:none https://github.com/continuedev/continue.git continue

WORKDIR /workspace/continue

# Checkout the base commit (before the fix)
RUN git checkout 7968dd106982ff5286df9a3915247d327b8a01e9

# Install root dependencies
RUN npm install --ignore-scripts 2>&1 | tail -5

# Install core dev dependencies (including jest)
RUN cd core && npm install --ignore-scripts --include=dev 2>&1 | tail -5

# Install and build dependencies in correct order (core depends on these packages)
# config-types has no internal dependencies
RUN cd packages/config-types && npm install --ignore-scripts --include=dev 2>&1 | tail -5
RUN cd packages/config-types && npm run build 2>&1 | tail -5

# config-yaml depends on config-types
RUN cd packages/config-yaml && npm install --ignore-scripts --include=dev 2>&1 | tail -5
RUN cd packages/config-yaml && npm run build 2>&1 | tail -5

# fetch has no internal dependencies
RUN cd packages/fetch && npm install --ignore-scripts --include=dev 2>&1 | tail -5
RUN cd packages/fetch && npm run build 2>&1 | tail -5

# llm-info has no internal dependencies
RUN cd packages/llm-info && npm install --ignore-scripts --include=dev 2>&1 | tail -5
RUN cd packages/llm-info && npm run build 2>&1 | tail -5

# terminal-security has no internal dependencies
RUN cd packages/terminal-security && npm install --ignore-scripts --include=dev 2>&1 | tail -5
RUN cd packages/terminal-security && npm run build 2>&1 | tail -5

# openai-adapters depends on config-types and fetch
RUN cd packages/openai-adapters && npm install --ignore-scripts --include=dev 2>&1 | tail -5
RUN cd packages/openai-adapters && npm run build 2>&1 | tail -5

# Create logs directory
RUN mkdir -p /logs/verifier

CMD ["bash"]