FROM golang:1.25-bookworm

# Install Python for test runner
RUN apt-get update && apt-get install -y python3 python3-pip git python3-pytest && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /workspace

# Clone Hugo repo at base commit
ARG BASE_COMMIT=45e4596630b1372ab02634e4536d2b5a89452e0b
RUN git clone --filter=blob:none https://github.com/gohugoio/hugo.git /workspace/hugo && \
    cd /workspace/hugo && \
    git checkout 45e4596630b1372ab02634e4536d2b5a89452e0b

# Install Go dependencies
RUN cd /workspace/hugo && go mod download

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Create directory for test.sh compatibility
RUN mkdir -p /workspace/task && ln -s /tests /workspace/task/tests

WORKDIR /workspace/hugo
