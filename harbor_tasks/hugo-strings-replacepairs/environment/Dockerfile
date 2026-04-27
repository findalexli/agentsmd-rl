FROM golang:1.25-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    GOFLAGS=-mod=mod \
    GOTOOLCHAIN=local

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/pyenv && \
    /opt/pyenv/bin/pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.3.5
ENV PATH="/opt/pyenv/bin:${PATH}"

WORKDIR /workspace
RUN git init /workspace/hugo && \
    cd /workspace/hugo && \
    git remote add origin https://github.com/gohugoio/hugo.git && \
    git fetch --depth=1 origin e3108225bf2f49bd3908614ac120bf1699fde241 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/hugo
RUN go mod download && \
    go build ./tpl/strings/... 2>/dev/null || true

RUN mkdir -p /logs/verifier

WORKDIR /workspace/hugo
