FROM golang:1.25-bookworm

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        git \
        python3 \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --break-system-packages \
        pytest==8.3.4

WORKDIR /workspace

ARG REPO_URL=https://github.com/pulumi/pulumi.git
ARG BASE_COMMIT=7db0e0eb20cf0d3e861c14dcfd34ce71448b138d

RUN git clone --filter=blob:none --no-checkout "${REPO_URL}" pulumi \
    && cd pulumi \
    && git fetch --depth=1 origin "${BASE_COMMIT}" \
    && git checkout "${BASE_COMMIT}"

ENV GOMODCACHE=/go/pkg/mod
ENV GOFLAGS=-mod=mod

RUN cd /workspace/pulumi/sdk \
    && go mod download \
    && go test -count=1 -run='^$' ./go/common/resource/plugin/...

RUN mkdir -p /logs/verifier

WORKDIR /workspace/pulumi
