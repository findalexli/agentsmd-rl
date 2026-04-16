FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest --break-system-packages

WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/excalidraw/excalidraw.git excalidraw

WORKDIR /workspace/excalidraw

# Checkout base commit (parent of merge commit)
RUN git checkout 0443511954a8a557866a98a939e2a506acb4858b

# Install dependencies
RUN yarn install --frozen-lockfile

RUN mkdir -p /logs/verifier
