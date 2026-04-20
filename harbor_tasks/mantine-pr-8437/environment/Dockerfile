FROM python:3.12-slim

WORKDIR /workspace

# Install git
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone mantine repo (full clone)
RUN git clone https://github.com/mantinedev/mantine.git mantine_repo

WORKDIR /workspace/mantine_repo

# Get base commit
RUN git checkout 0c52227db887ce0b48fe59fa3422638b0448e1e1

# Create symlink for workspace
RUN ln -s /workspace/mantine_repo /workspace/mantine

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/mantine_repo
