FROM golang:1.24-bookworm

# Enable GOTOOLCHAIN to auto-download required Go version
ENV GOTOOLCHAIN=auto

# Install Python for test runner
RUN apt-get update && apt-get install -y python3 python3-pip python3-pytest git && rm -rf /var/lib/apt/lists/*

# Configure pip to allow system packages installation
RUN mkdir -p /root/.config/pip && echo "[global]\nbreak-system-packages = true" > /root/.config/pip/pip.conf

# Set up workspace
WORKDIR /workspace
RUN mkdir -p /logs/verifier

# Clone Hugo repo at base commit (before the fix)
ARG BASE_COMMIT=0c013c2326be1bbebba9a9f89d27072074fc6cc4
RUN git clone --filter=blob:none https://github.com/gohugoio/hugo.git /workspace/hugo && \
    cd /workspace/hugo && \
    git checkout ${BASE_COMMIT}

# Pre-download Go modules to speed up tests
RUN cd /workspace/hugo && go mod download

# Set working directory
WORKDIR /workspace/hugo

# Create expected directory structure for tests (test.sh expects /workspace/task)
RUN mkdir -p /workspace/task && ln -sf /tests /workspace/task/tests
