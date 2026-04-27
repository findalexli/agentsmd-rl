FROM golang:1.26-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV GOFLAGS=-mod=mod
ENV CGO_ENABLED=0

# python3 is required by the harbor pytest runner; git is needed to apply patches.
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# pytest for the verifier (kept in a venv so it never collides with system pip).
RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir \
        pytest==8.3.4
ENV PATH="/opt/venv/bin:${PATH}"

# Clone the vitess source tree at the PR's base commit (parent of the merge commit).
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/vitessio/vitess.git \
    && cd vitess \
    && git checkout ef3aa669e2acef95e4751f097115b0d230aa8015 \
    && git config user.email "task@example.com" \
    && git config user.name "task"

WORKDIR /workspace/vitess

# Pre-fetch Go module dependencies and pre-compile the reparentutil package and
# its transitive deps so test runs at evaluation time don't need network access.
RUN go mod download \
    && go test -count=0 ./go/vt/vtctl/reparentutil/... \
    && go vet ./go/vt/vtctl/reparentutil/...

# Cache build artifacts that persist into derived images.
ENV GOCACHE=/root/.cache/go-build
ENV GOMODCACHE=/go/pkg/mod

RUN mkdir -p /logs/verifier

# Mark a fresh git baseline so test_outputs.py can apply the test patch
# cleanly (and reset it between runs) without seeing a dirty tree.
RUN git add -A && git commit -m "baseline" --allow-empty
