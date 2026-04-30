FROM golang:1.25.1-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV GOFLAGS=-mod=mod
ENV CGO_ENABLED=0

RUN apt-get update && apt-get install -y --no-install-recommends \
    git=1:2.39.5-0+deb12u2 \
    ca-certificates \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

RUN git init /workspace/hugo && \
    cd /workspace/hugo && \
    git remote add origin https://github.com/gohugoio/hugo.git && \
    git fetch --depth=1 origin e8577771c3275d16b7d1b31cca5e9fd3ea517416 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/hugo

RUN go mod download

RUN go build ./...

RUN go test -count=1 -run NOMATCH_PRECOMPILE ./hugolib/ >/dev/null 2>&1 || true

RUN pip install --no-cache-dir --break-system-packages \
    pytest==8.3.4

RUN mkdir -p /logs/verifier

WORKDIR /workspace/hugo
