FROM node:22-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone VS Code repo at the base commit (pre-fix)
ENV BASE_COMMIT=0dad7e0453d4d5a72113c59e8220aaf45020b9e7
RUN git init /workspace/vscode && \
    cd /workspace/vscode && \
    git remote add origin https://github.com/microsoft/vscode && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Sanitize: remove .git history but keep the code
RUN cd /workspace/vscode && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent" && \
    git commit -m "snapshot at base commit"

# Set up environment
WORKDIR /workspace/vscode

# Create logs directory for test results
RUN mkdir -p /logs/verifier
