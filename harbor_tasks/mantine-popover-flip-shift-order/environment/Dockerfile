FROM node:22-slim

# Install python3 for pytest runner
RUN apt-get update && apt-get install -y python3 python3-pip python3-pytest git && rm -rf /var/lib/apt/lists/*

# Clone the mantine repo at base commit
ARG BASE_COMMIT=5cda4fb4a2dcd36f518a91f5f45a50ebaada8ee2
RUN git clone --filter=blob:none https://github.com/mantinedev/mantine.git /workspace/mantine \
    && cd /workspace/mantine \
    && git checkout ${BASE_COMMIT}

WORKDIR /workspace/mantine

# Install dependencies
RUN yarn install --frozen-lockfile

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
