FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip install pytest --quiet

WORKDIR /workspace

# Clone the repo (shallow, just what we need)
RUN git clone --filter=blob:none --depth=1 https://github.com/effect-ts/effect.git

WORKDIR /workspace/effect

# Checkout the base commit
RUN git checkout 590dbfc942277fe2be68cf9a81b40335c6640821

RUN mkdir -p /logs/verifier

# Just clone and checkout - no install needed for source-level tests
# The tests verify the source code contains the fix