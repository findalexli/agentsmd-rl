FROM node:22-slim

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    tmux \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Clone VS Code repo at the specific commit (base commit before the revert PR)
# This is the commit that has the theme auto-update notification (the code we need to REMOVE)
RUN git clone --depth 1 https://github.com/microsoft/vscode.git vscode
WORKDIR /workspace/vscode

# Fetch and checkout the specific base commit (the one that has the notification code)
# Commit d4b002af75f1878ead5b608beed470b9ae25b6f8 has the showThemeAutoUpdatedNotification method
RUN git fetch --depth=1 origin d4b002af75f1878ead5b608beed470b9ae25b6f8 && \
    git checkout d4b002af75f1878ead5b608beed470b9ae25b6f8

# Sanitize: remove .git history but keep the source tree
# This creates a snapshot that can't be accidentally git-pulled
RUN rm -rf .git && \
    git init && \
    git add -A && \
    git -c user.email="test@example.com" -c user.name="Test" commit -m "Initial snapshot"

# Install minimal dependencies for TypeScript compilation
RUN npm ci --ignore-scripts 2>/dev/null || npm install --ignore-scripts 2>/dev/null || true

# Create log directory
RUN mkdir -p /logs/verifier

# Configure git user for any future git operations
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

WORKDIR /workspace/vscode
