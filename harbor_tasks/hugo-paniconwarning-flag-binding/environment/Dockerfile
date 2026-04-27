FROM golang:1.25-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    CGO_ENABLED=0 \
    GOFLAGS=-mod=mod \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --break-system-packages --no-cache-dir \
        pytest==8.3.4

WORKDIR /workspace

RUN git init /workspace/hugo && \
    cd /workspace/hugo && \
    git remote add origin https://github.com/gohugoio/hugo.git && \
    git fetch --depth=1 origin ab62320d6bceece0faa7029f8bd79d546d0f64be && \
    git checkout FETCH_HEAD

WORKDIR /workspace/hugo

RUN go mod download

RUN go build -o /tmp/hugo-warm ./ && rm -f /tmp/hugo-warm

RUN go vet ./commands/...

RUN mkdir -p /logs/verifier
