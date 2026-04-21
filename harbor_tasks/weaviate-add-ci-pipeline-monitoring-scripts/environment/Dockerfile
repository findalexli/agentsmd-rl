FROM golang:1.25-alpine

# Install Python for the test runner and basic tools
RUN apk add --no-cache python3 py3-pip py3-pytest git patch bash curl

# Create necessary directories
RUN mkdir -p /logs/verifier

# Clone weaviate repo at base commit (before PR #10542)
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/weaviate/weaviate.git weaviate && \
    cd weaviate && \
    git checkout 57d1e03321fd1648889b5c3fae5261cf5a7a0217

WORKDIR /workspace/weaviate

# Configure git
RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Test Agent"

# Download Go module dependencies
RUN go mod download
