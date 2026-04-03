FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 tmux unzip && \
    rm -rf /var/lib/apt/lists/*

# Install bun
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:$PATH"

# Clone opencode at base commit (before fix)
RUN git init /workspace/opencode && \
    cd /workspace/opencode && \
    git remote add origin https://github.com/anomalyco/opencode.git && \
    git fetch --depth=1 origin 771525270a0c4d1394b3117e5842847a51caf72d && \
    git checkout FETCH_HEAD

# Configure git
RUN cd /workspace/opencode && \
    git config user.email "agent@test.com" && \
    git config user.name "Agent"

# Install dependencies
RUN cd /workspace/opencode && bun install

RUN mkdir -p /logs/verifier

WORKDIR /workspace/opencode