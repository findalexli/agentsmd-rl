FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# Install system deps including python3 for pytest, and gh CLI for workflow testing
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential \
        python3 python3-pip python3-venv \
        gnupg lsb-release && \
    # Install GitHub CLI (gh)
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | \
        gpg --dearmor -o /usr/share/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | \
        tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
    apt-get update && \
    apt-get install -y gh && \
    rm -rf /var/lib/apt/lists/*

# Install Bun (required by this repo)
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:${PATH}"

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/anomalyco/opencode.git /workspace/opencode && \
    cd /workspace/opencode && \
    git checkout 31f893f8cb7cbec11ae743b4ead806c201a396b7 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/opencode

# Install minimal deps needed by test_outputs.py (PyYAML for parsing workflow files)
RUN pip3 install --no-cache-dir pyyaml --break-system-packages 2>/dev/null || \
    pip3 install --no-cache-dir pyyaml

# Verifier output directory
RUN mkdir -p /logs/verifier
