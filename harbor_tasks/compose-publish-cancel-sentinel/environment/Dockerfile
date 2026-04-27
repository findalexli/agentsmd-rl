FROM golang:1.25-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    GOFLAGS="-mod=mod" \
    GOPROXY=https://proxy.golang.org,direct

RUN apt-get update -qq \
 && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
 && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --break-system-packages \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1

WORKDIR /workspace
RUN git init /workspace/compose && \
    cd /workspace/compose && \
    git remote add origin https://github.com/docker/compose.git && \
    git fetch --depth=1 origin 3d2d03cd39145a8cb29ac3c5440172d994834111 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/compose

RUN go mod download

RUN mkdir -p /logs/verifier
