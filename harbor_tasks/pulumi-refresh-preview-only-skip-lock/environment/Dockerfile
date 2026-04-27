FROM golang:1.25.8-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    GO111MODULE=on \
    CGO_ENABLED=1 \
    GOFLAGS=-mod=mod

RUN apt-get update && apt-get install -y --no-install-recommends \
        git ca-certificates curl python3 python3-pip python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir pytest==8.3.4

ENV PATH="/opt/venv/bin:${PATH}"

WORKDIR /workspace

ARG REPO_URL=https://github.com/pulumi/pulumi
ARG BASE_COMMIT=d6f3e3a290907239b9ec6f94b4a05af33a70db17

RUN git clone --filter=blob:none "${REPO_URL}" /workspace/pulumi \
    && cd /workspace/pulumi \
    && git checkout "${BASE_COMMIT}"

# Drop in the harness test file. This file is part of the test harness, NOT
# the gold solution — it exists at the base commit so the test can run
# without modification, regardless of whether the agent has applied the fix.
COPY preview_only_test.go /workspace/pulumi/pkg/backend/diy/preview_only_test.go

# Pre-fetch dependencies so go test does not hit the network at run time.
RUN cd /workspace/pulumi/pkg \
    && go mod download \
    && cd /workspace/pulumi/sdk \
    && go mod download

# Pre-compile the diy package and its tests so the agent's first
# `go test` invocation does not pay the full cost.
RUN cd /workspace/pulumi/pkg \
    && go test -count=1 -run=^$ ./backend/diy/... >/dev/null 2>&1 || true

RUN mkdir -p /logs/verifier

WORKDIR /workspace/pulumi
