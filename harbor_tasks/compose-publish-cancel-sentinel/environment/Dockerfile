FROM golang:1.25-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    GOFLAGS="-mod=mod" \
    GOPROXY=https://proxy.golang.org,direct

RUN apt-get update -qq \
 && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
 && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --break-system-packages \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1

WORKDIR /workspace
RUN git init /workspace/compose && \
    cd /workspace/compose && \
    git remote add origin https://github.com/docker/compose.git && \
    git fetch --depth=1 origin 3d2d03cd39145a8cb29ac3c5440172d994834111 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/compose

RUN go mod download

# Install golangci-lint matching the project version (v2.11.3 from repo Dockerfile ARG).
# Pinned binary release URL for reproducibility — GitHub release artifacts are immutable.
RUN curl -fsSL https://github.com/golangci/golangci-lint/releases/download/v2.11.3/golangci-lint-2.11.3-linux-amd64.tar.gz \
    | tar -xz -C /tmp && \
    mv /tmp/golangci-lint-2.11.3-linux-amd64/golangci-lint /usr/local/bin/golangci-lint && \
    rm -rf /tmp/golangci-lint-2.11.3-linux-amd64 && \
    golangci-lint --version

RUN mkdir -p /logs/verifier
