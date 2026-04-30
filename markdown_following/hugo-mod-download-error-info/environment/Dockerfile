FROM golang:1.25-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV GOFLAGS="-mod=mod"
ENV CGO_ENABLED=0

RUN apt-get update && apt-get install -y --no-install-recommends \
        git=1:2.39.* \
        ca-certificates \
        python3=3.11.* \
        python3-pip \
        bc \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --break-system-packages --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1

WORKDIR /workspace

RUN git init /workspace/hugo && \
    cd /workspace/hugo && \
    git remote add origin https://github.com/gohugoio/hugo.git && \
    git fetch --depth=1 origin a18bec1123e582da818dc8a841285d1a8eb27de4 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/hugo

# Pre-download Go module deps so the test runner doesn't need to during execution.
RUN go mod download

# Verify the build works on the base commit (smoke test).
RUN go build ./modules/... ./hugolib/...

RUN mkdir -p /logs/verifier
