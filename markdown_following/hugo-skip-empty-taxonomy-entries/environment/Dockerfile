FROM golang:1.25.0-bookworm

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages --no-cache-dir pytest==8.3.4

ENV CGO_ENABLED=1 \
    GOFLAGS=-mod=mod \
    GOPROXY=https://proxy.golang.org,direct

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/gohugoio/hugo.git
WORKDIR /workspace/hugo
RUN git checkout cc338a9d4854c7e7273a5c3c8fee436c642f4dde

# Pre-fetch Go modules to avoid network at test time.
RUN go mod download

# Compile-test-cache hugolib so the first `go test` at run-time is faster.
RUN go test -run NONE -count=1 ./hugolib/ ./config/allconfig/... >/dev/null 2>&1 || true
RUN go vet ./config/allconfig/... >/dev/null 2>&1 || true

RUN mkdir -p /logs/verifier
