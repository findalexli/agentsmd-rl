FROM golang:1.24-bookworm

# Install Python for pytest
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*

# Install Hugo v0.146.0 (version at base commit)
RUN go install github.com/gohugoio/hugo@v0.146.0

# Clone the Hugo repository at base commit
ARG REPO=gohugoio/hugo
ARG BASE_COMMIT=06fcb724219eecdc20367e86e1a8134d3d7e0e5b

WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/${REPO}.git hugo && \
    cd hugo && \
    git checkout ${BASE_COMMIT}

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/hugo
