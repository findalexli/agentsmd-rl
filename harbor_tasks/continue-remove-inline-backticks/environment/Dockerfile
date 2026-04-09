FROM node:22-slim

# Install Python for pytest runner
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create workspace and logs directories
WORKDIR /workspace
RUN mkdir -p /logs/verifier

# Clone the repo at the base commit
ARG REPO=continue
ARG REPO_URL=https://github.com/continuedev/continue.git
ARG BASE_COMMIT=b09c4ba1f3438bd29b5556a52d81fa5463134fd3

RUN git clone --filter=blob:none $REPO_URL $REPO && \
    cd $REPO && \
    git checkout $BASE_COMMIT

# Install dependencies (needed for TypeScript compilation checks)
WORKDIR /workspace/continue
RUN npm ci || npm install

WORKDIR /workspace
