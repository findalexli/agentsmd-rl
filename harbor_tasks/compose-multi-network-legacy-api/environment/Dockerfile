FROM golang:1.25.8-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    GOFLAGS=-mod=mod \
    GOTOOLCHAIN=local \
    CGO_ENABLED=0

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        git \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"
RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1

WORKDIR /workspace
RUN git init /workspace/compose && \
    cd /workspace/compose && \
    git remote add origin https://github.com/docker/compose.git && \
    git fetch --depth=1 origin 9cab43945a5ad651190ce5ec9800f449f489b5f6 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/compose

# Pre-download Go module dependencies and warm the build cache so agent / test
# runs do not need network. We compile the test binary up-front to populate the
# cache (the binary itself is removed).
RUN go mod download && \
    go build ./... && \
    go test -c -o /tmp/compose-pkg.test ./pkg/compose/ && \
    rm -f /tmp/compose-pkg.test

RUN mkdir -p /logs/verifier
