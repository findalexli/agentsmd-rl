FROM node:22-slim

# Install Python for pytest runner
RUN apt-get update && apt-get install -y python3 python3-pip git && rm -rf /var/lib/apt/lists/*

# Install pnpm globally (repo uses pnpm)
RUN npm install -g pnpm@9

# Clone the repo at base commit
ARG BASE_COMMIT=5b0a4378f4bc5613ffc499c4781c549570799fbd
RUN git clone --filter=blob:none https://github.com/trpc/trpc.git /workspace/trpc && \
    cd /workspace/trpc && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/trpc

# Install dependencies using pnpm
RUN pnpm install --frozen-lockfile

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default shell
CMD ["/bin/bash"]
