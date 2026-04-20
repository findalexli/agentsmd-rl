FROM node:22-slim

WORKDIR /workspace

# Install git and basic build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install yarn globally (force to handle existing installation)
RUN npm install -g yarn@1.22.22 --force

# Clone the repository (base commit)
RUN git clone --filter=blob:none --no-checkout https://github.com/reduxjs/redux-toolkit.git
WORKDIR /workspace/redux-toolkit
RUN git checkout ad2b2882075bd7a2fc8bb7cdf271315524d7cbfd

# Install dependencies
RUN yarn install --frozen-lockfile 2>/dev/null || yarn install

# Install pytest for test runner
RUN pip3 install pytest==8.3.4 --break-system-packages

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace
