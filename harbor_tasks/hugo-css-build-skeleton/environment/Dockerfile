FROM golang:1.25-bookworm

# Install Python and pip for test runner
RUN apt-get update && apt-get install -y python3 python3-pip git && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the Hugo repository at the base commit (parent of merge commit)
# Base commit: 06fcb724219eecdc20367e86e1a8134d3d7e0e5b
RUN git clone --filter=blob:none https://github.com/gohugoio/hugo.git && \
    cd hugo && \
    git checkout 06fcb724219eecdc20367e86e1a8134d3d7e0e5b

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default working directory for the task
WORKDIR /workspace/hugo
