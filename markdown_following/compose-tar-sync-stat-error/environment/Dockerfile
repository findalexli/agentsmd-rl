FROM golang:1.25.8-bookworm

ARG DEBIAN_FRONTEND=noninteractive
ENV CGO_ENABLED=0 \
    GOFLAGS=-mod=mod \
    GOTOOLCHAIN=local

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-venv \
        git \
        ca-certificates \
        curl \
        bash \
        util-linux \
        sudo \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --break-system-packages --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1

RUN curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/v2.11.3/install.sh \
        | sh -s -- -b /usr/local/bin v2.11.3 \
    && golangci-lint --version

RUN useradd -m -u 1002 -s /bin/bash runner \
    && mkdir -p /workspace /go-cache /logs/verifier \
    && chown -R runner:runner /workspace /go-cache /logs/verifier

WORKDIR /workspace

USER runner

ENV GOPATH=/go-cache \
    GOCACHE=/go-cache/build \
    GOMODCACHE=/go-cache/mod \
    HOME=/home/runner

RUN git init /workspace/compose && \
    cd /workspace/compose && \
    git remote add origin https://github.com/docker/compose.git && \
    git fetch --depth=1 origin c1aefc74c84c3d1afe83dfc95cf61c12844f45b9 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/compose

RUN go mod download \
    && go build ./internal/sync/... \
    && go vet ./internal/sync/...

USER root
RUN mkdir -p /logs/verifier && chmod 0777 /logs/verifier
USER runner

WORKDIR /workspace/compose
