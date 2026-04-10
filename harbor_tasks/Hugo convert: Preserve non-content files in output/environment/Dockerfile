FROM golang:bookworm

# Install Python for pytest
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    python3-pytest \
    && rm -rf /var/lib/apt/lists/*

# Create logs directory
RUN mkdir -p /logs/verifier /workspace/task && ln -s /tests /workspace/task/tests

# Clone Hugo at the base commit (shallow clone with full history for the commit)
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/gohugoio/hugo.git hugo && \
    cd hugo && \
    git checkout d88a29e002ebc31bf9b4e1e024f141cc0b39a657

WORKDIR /workspace/hugo

# Download Go module dependencies
RUN go mod download

# Install hugo binary temporarily (needed for tests)
RUN go build -o /usr/local/bin/hugo .

WORKDIR /workspace
