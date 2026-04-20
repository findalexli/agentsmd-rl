FROM node:22-slim

WORKDIR /workspace

# Install python3, pip, and git for pytest and repo cloning
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install pytest and requests for the test harness
RUN pip3 install --no-cache-dir --break-system-packages pytest==8.3.4 requests==2.32.3

# Enable yarn via corepack
RUN corepack enable && corepack prepare yarn@4.10.3 --activate

# Clone mantine repo at the base commit (filter for no blobs to save bandwidth)
RUN git clone --filter=blob:none --no-checkout https://github.com/mantinedev/mantine.git
WORKDIR /workspace/mantine
RUN git checkout 5cda4fb4a2dcd36f518a91f5f45a50ebaada8ee2

# Install dependencies using yarn (workspace)
RUN yarn install --immutable

# Install tsx for running TypeScript scripts
RUN npm install -g tsx@4.20.5

WORKDIR /workspace
