FROM golang:1.25-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    GOFLAGS="-mod=mod" \
    GOTOOLCHAIN=local

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        python3 \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --break-system-packages \
        pytest==8.3.4 \
        pytest-json-report==1.5.0

WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/docker/compose.git /workspace/compose
WORKDIR /workspace/compose
RUN git checkout 3d2d03cd39145a8cb29ac3c5440172d994834111

RUN go mod download
RUN go build ./pkg/compose/...

RUN mkdir -p /logs/verifier
