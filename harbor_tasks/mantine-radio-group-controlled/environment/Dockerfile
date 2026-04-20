FROM python:3.12-slim

# Install Node.js 20 and yarn
RUN apt-get update && apt-get install -y curl git \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g corepack \
    && corepack enable yarn \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone the repo at the base commit (shallow clone)
RUN git clone --filter=blob:none --no-checkout https://github.com/mantinedev/mantine.git \
    && cd mantine \
    && git checkout 17bd67fcba7996750466583caadc5453212ad23e

WORKDIR /workspace/mantine

# Install dependencies using yarn
RUN yarn install --immutable

# Install pytest for test harness
RUN pip install --no-cache-dir pytest==8.3.4 pytest-timeout==2.3.1

# Create logs directory
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]