FROM golang:1.25-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV GOFLAGS=-mod=mod
ENV CGO_ENABLED=0

# System tools used by tests/solve.sh: git for the working tree, python3 for
# the pytest harness. patch is used by solve.sh to apply the gold diff.
RUN apt-get update && apt-get install -y --no-install-recommends \
        git=1:2.39.* \
        ca-certificates \
        python3=3.11.* \
        python3-pip=23.* \
        patch=2.7.* \
    && rm -rf /var/lib/apt/lists/*

# Pinned pytest stack — versions match what the harness expects.
RUN pip install --no-cache-dir --break-system-packages \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1

WORKDIR /workspace

# Shallow-clone the repo at the base commit. depth=1 keeps the image small.
RUN git init /workspace/pulumi && \
    cd /workspace/pulumi && \
    git remote add origin https://github.com/pulumi/pulumi.git && \
    git fetch --depth=1 origin 0a0aff442aaed8995df679b11214c414799fba31 && \
    git checkout FETCH_HEAD \
    && git config user.email "task@example.com" \
    && git config user.name  "Task Runner"

# Pre-download Go modules for the pkg module so the test run is offline-fast.
WORKDIR /workspace/pulumi/pkg
RUN go mod download

# Pre-compile the pkg/backend/display package and its test deps. This
# populates the build cache so `go test` inside the container is fast and
# does NOT need network access.
RUN go test -count=1 -run '^$' ./backend/display/... || true

WORKDIR /workspace/pulumi

RUN mkdir -p /logs/verifier

CMD ["/bin/bash"]
