FROM node:22-slim

# Install Python for pytest
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace
RUN mkdir -p /logs/verifier

# Clone repo at base commit (shallow clone for speed)
RUN git clone --depth=50 --filter=blob:none https://github.com/continuedev/continue.git continuedev_continue && \
    cd continuedev_continue && \
    git checkout e8c88f416fe0be8f9fc9e92c2f2adab82fb023d4

# Install dependencies
WORKDIR /workspace/continuedev_continue/gui
RUN npm ci 2>/dev/null || npm install

# Verify TypeScript compilation works
RUN npx tsc --noEmit 2>/dev/null || echo "TypeScript check may require build steps"
