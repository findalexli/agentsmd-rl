FROM python:3.12-slim

WORKDIR /workspace

# Install Node.js, git, and other dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    nodejs \
    npm \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN npm install -g pnpm@8

# Clone repository with depth for merge commit access
RUN git clone --filter=blob:none --no-checkout https://github.com/mantinedev/mantine.git
WORKDIR /workspace/mantine
RUN git checkout 08057a653eec5e671451db7113e5b8a46f16de29

# Install dependencies
RUN pnpm install --no-frozen-lockfile

# Install pytest for test runner
RUN pip install pytest==8.3.4 --break-system-packages

# Create logs directory
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]