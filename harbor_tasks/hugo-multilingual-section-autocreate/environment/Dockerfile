FROM golang:1.25.9-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV GOFLAGS="-mod=mod"
ENV GOTOOLCHAIN=local

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-venv \
        git \
        ca-certificates \
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
    git fetch --depth=1 origin 0755872424182a99520ab27f54df29ba2bcccddc && \
    git checkout FETCH_HEAD \
    && git config user.email "test@example.com" \
    && git config user.name "Test"

WORKDIR /workspace/hugo

RUN go mod download

# Pre-build the hugolib test binary so first invocation isn't a cold compile.
# We compile-only (-c) and discard; the cached object files speed up later runs.
RUN go test -count=1 -c -o /tmp/hugolib_test ./hugolib/ && rm -f /tmp/hugolib_test

RUN mkdir -p /logs/verifier
