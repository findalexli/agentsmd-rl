FROM node:22-slim

WORKDIR /workspace

# Install git, python3, and pnpm
RUN apt-get update && apt-get install -y --no-install-recommends git python3 python3-pip
RUN npm install -g pnpm@10

# Clone repository (shallow clone for speed)
RUN git clone --filter=blob:none --no-checkout https://github.com/prisma/prisma.git

WORKDIR /workspace/prisma
RUN git checkout 1a3c4986d8c560d87a388a7545371138bcc8f5a1

# Install dependencies
RUN pnpm install --frozen-lockfile

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create log directory
RUN mkdir -p /logs/verifier
