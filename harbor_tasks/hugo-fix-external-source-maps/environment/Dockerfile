FROM golang:1.25.0-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    GOFLAGS=-mod=mod \
    CGO_ENABLED=0

RUN apt-get update && apt-get install -y --no-install-recommends \
        git=1:2.39.5-0+deb12u2 \
        ca-certificates=20230311+deb12u1 \
        python3=3.11.2-1+b1 \
        python3-pip=23.0.1+dfsg-1 \
        python3-venv=3.11.2-1+b1 \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --break-system-packages --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.3.5

WORKDIR /workspace

RUN git init /workspace/hugo && \
    cd /workspace/hugo && \
    git remote add origin https://github.com/gohugoio/hugo.git && \
    git fetch --depth=1 origin a7cbcf15f0c5ef04b45350390e00e584e4d635b9 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/hugo

# Pre-fetch Go module dependencies and warm the build cache for the
# packages our tests will exercise. Significantly cuts test wallclock.
RUN go mod download \
    && go build ./internal/js/esbuild \
    && go test -count=1 -run NoMatchPlaceholder ./internal/js/esbuild \
    && go test -count=1 -run NoMatchPlaceholder ./tpl/css \
    && go test -count=1 -run NoMatchPlaceholder ./resources/resource_transformers/js

RUN mkdir -p /logs/verifier

ENV REPO=/workspace/hugo
