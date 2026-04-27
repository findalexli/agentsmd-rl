FROM node:22-slim

# Install Python 3, pip, and git for pytest runner and patching
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 python3-pip git ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Install pytest (pinned)
RUN pip3 install --break-system-packages pytest==8.3.4

# Clone repository
RUN git clone --filter=blob:none https://github.com/BerriAI/litellm.git /workspace/litellm

WORKDIR /workspace/litellm

# Checkout base commit (parent of merge commit 24886394b35e5c12b98e5b6d41ddfb8b3ee9d051)
RUN git checkout c898edbd14b82f5f93a77d1b12a1e2a80af71a62

# Install UI dashboard dependencies
WORKDIR /workspace/litellm/ui/litellm-dashboard
RUN npm ci 2>/dev/null || npm install

# Create log directories
RUN mkdir -p /logs/verifier

WORKDIR /workspace/litellm
