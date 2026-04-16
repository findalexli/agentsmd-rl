FROM node:22-slim

# Install python3 and pytest for test runner
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv git && \
    rm -rf /var/lib/apt/lists/* && \
    python3 -m pip install pytest --break-system-packages

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Increase Node.js memory limit
ENV NODE_OPTIONS="--max-old-space-size=4096"

WORKDIR /workspace

# Clone ant-design with filter for performance
RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git ant-design

WORKDIR /workspace/ant-design

# Checkout base commit (before the fix)
RUN git checkout 9702dbb57d3cb8ce4346b96c895e6fd6f43e56d3

# Install dependencies (skip optional deps to save space/time)
RUN npm install --legacy-peer-deps --ignore-scripts

# Install tsx for running TypeScript directly without full build
RUN npm install -g tsx

# Generate version file (required for module imports)
RUN npx tsx scripts/generate-version.ts

WORKDIR /workspace/ant-design
