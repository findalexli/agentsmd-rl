FROM node:24-slim

RUN apt-get update && apt-get install -y git python3 python3-pip

WORKDIR /workspace

# Clone mantine repo
RUN git clone --filter=blob:none --depth=1 https://github.com/mantinedev/mantine.git

WORKDIR /workspace/mantine

# Checkout base commit (before the fix)
RUN git checkout d3ca1bcb9f872673aca275b944aa2c7e55666c4e

# Enable corepack and use yarn 4.10.3
RUN corepack enable && corepack prepare yarn@4.10.3 --activate

# Install dependencies
RUN yarn install --immutable

# Install pytest for running tests
RUN pip install --no-cache-dir --break-system-packages pytest==8.3.4

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/mantine