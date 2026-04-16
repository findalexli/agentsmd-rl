FROM golang:1.25-alpine

# Install dependencies
RUN apk add --no-cache git bash python3 py3-pip patch

# Set working directory
WORKDIR /workspace

# Clone Hugo repo at base commit
RUN git clone --filter=blob:none https://github.com/gohugoio/hugo.git /workspace/hugo && \
    cd /workspace/hugo && \
    git checkout d88a29e002ebc31bf9b4e1e024f141cc0b39a657

# Install Python pytest for test runner
RUN pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/hugo
