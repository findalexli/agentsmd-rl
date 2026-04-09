FROM node:22-slim

# Install Python for pytest test runner
RUN apt-get update && apt-get install -y python3 python3-pip git && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

WORKDIR /workspace

# Clone the repo at the base commit (before the fix)
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router && \
    cd router && \
    git checkout 30835cb8e935b740c92fa95909a073e644dde530

# Install dependencies
RUN cd router && npm install -g pnpm && pnpm install

# Create logs directory for verifier
RUN mkdir -p /logs/verifier
