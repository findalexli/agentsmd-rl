FROM golang:1.26.1-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    GOFLAGS="-mod=mod" \
    GOTOOLCHAIN=local

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-venv \
        git \
        ca-certificates \
        bash \
        coreutils \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-report==1.5.0 \
        pyyaml==6.0.2

WORKDIR /workspace

RUN git init /workspace/vitess && \
    cd /workspace/vitess && \
    git remote add origin https://github.com/vitessio/vitess.git && \
    git fetch --depth=1 origin 9a3646f7f16d38cec2efabc13cef5da800a72280 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/vitess

RUN cd go/vt/sqlparser \
    && go mod download \
    && go test -count=1 -run XXX_NoSuchTest_XXX ./... >/dev/null 2>&1 || true \
    && go vet ./... >/dev/null 2>&1 || true

RUN mkdir -p /logs/verifier

ENV REPO=/workspace/vitess \
    SQLPARSER=/workspace/vitess/go/vt/sqlparser
