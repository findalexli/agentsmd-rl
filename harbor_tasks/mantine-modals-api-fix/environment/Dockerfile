FROM node:22-slim

# Install Python for pytest
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the mantine repo at base commit (the buggy state)
# Base commit is the parent of merge commit: 6cfca290cd5535c031531fa872a6058a625351c0
RUN git clone --filter=blob:none https://github.com/mantinedev/mantine.git && \
    cd mantine && \
    git checkout 6cfca290cd5535c031531fa872a6058a625351c0

# Install dependencies for the modals package
WORKDIR /workspace/mantine
RUN yarn install --frozen-lockfile || npm install

# Create verifier logs directory
RUN mkdir -p /logs/verifier

# Set working directory for tests
WORKDIR /workspace/mantine
