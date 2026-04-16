FROM golang:1.25-alpine

# Install python, git, and basic tools needed for testing
# Install pytest via apk to avoid PEP 668 issues
RUN apk add --no-cache python3 py3-pytest git bash curl

# Create workspace
WORKDIR /workspace

# Clone Hugo repo at the base commit (before the fix)
# Using --filter=blob:none for faster clone
RUN git clone --filter=blob:none https://github.com/gohugoio/hugo.git hugo && \
    cd hugo && \
    git checkout 481baa08968e29e2a2771e9d6022c9f995b2fc11

# Download Go dependencies
RUN cd /workspace/hugo && go mod download

# Create logs directory
RUN mkdir -p /logs/verifier

# Set working directory for tests
WORKDIR /workspace/hugo
