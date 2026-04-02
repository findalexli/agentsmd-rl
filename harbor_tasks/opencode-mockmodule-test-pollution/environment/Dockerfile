FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl unzip ca-certificates build-essential python3 tmux && \
    rm -rf /var/lib/apt/lists/*

# Install Bun
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:$PATH"

# Clone opencode at base commit (before fix)
RUN git clone https://github.com/anomalyco/opencode.git /workspace/opencode && \
    cd /workspace/opencode && \
    git checkout e973bbf54a519566bfdccce3474178b26b163a6d

# Configure git
RUN cd /workspace/opencode && \
    git config user.email "agent@test.com" && \
    git config user.name "Agent"

# Install dependencies (needed to run tests)
RUN cd /workspace/opencode && bun install --frozen-lockfile || \
    cd /workspace/opencode && bun install

RUN mkdir -p /logs/verifier

WORKDIR /workspace/opencode