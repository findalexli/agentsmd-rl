FROM golang:1.25.0-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    GOFLAGS=-mod=mod \
    CGO_ENABLED=1 \
    GO111MODULE=on

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"
RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-report==1.5.0

WORKDIR /workspace

RUN git init /workspace/hugo && \
    cd /workspace/hugo && \
    git remote add origin https://github.com/gohugoio/hugo.git && \
    git fetch --depth=1 origin 13a95b9c0167c832fe2babf961ac5cad22e3a1e4 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/hugo

RUN go mod download

RUN go test -count=0 ./hugolib/ ./tpl/tplimpl/ >/dev/null 2>&1 || true

RUN mkdir -p /logs/verifier
