FROM php:8.3-cli-slim

# Install Python3 and pip for pytest
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create working directories
WORKDIR /workspace
RUN mkdir -p /logs/verifier

# Clone the appwrite repo at the base commit
# Using --filter=blob:none for shallow clone of large repo
RUN git clone --filter=blob:none --no-checkout https://github.com/appwrite/appwrite.git appwrite \
    && cd appwrite \
    && git sparse-checkout init --cone \
    && git sparse-checkout set app/controllers \
    && git checkout 9ac686ae318e63d7a159d7a4021e8a786ee4972b

WORKDIR /workspace/appwrite
