FROM golang:1.23-alpine

# Install dependencies
RUN apk add --no-cache git python3 py3-pip py3-yaml py3-pytest curl jq patch bash

# Create logs directory
RUN mkdir -p /logs/verifier

# Clone the Hugo repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/gohugoio/hugo.git hugo

WORKDIR /workspace/hugo
RUN git checkout 3315a86d67dafda106eb8e422f8aebff67bff92d

# Set environment to allow automatic toolchain selection
ENV GO111MODULE=on
ENV CGO_ENABLED=0
ENV GOTOOLCHAIN=auto

# Download Go modules (Go will auto-download newer toolchain if needed)
RUN go mod download || true
