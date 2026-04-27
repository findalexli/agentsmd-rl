FROM golang:1.23-bookworm

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages \
    pytest==8.3.4 \
    pytest-json-report==1.5.0

ENV GOPATH=/go
ENV GOCACHE=/root/.cache/go-build
ENV PATH=$GOPATH/bin:$PATH

WORKDIR /workspace
RUN git init /workspace/sentry-go && \
    cd /workspace/sentry-go && \
    git remote add origin https://github.com/getsentry/sentry-go.git && \
    git fetch --depth=1 origin c24b7484373c2a3afc81e7cffd33f24a6bcc8ece && \
    git checkout FETCH_HEAD

WORKDIR /workspace/sentry-go

# Pre-fetch Go module deps for offline test runs
RUN go mod download && go vet ./... > /dev/null 2>&1 || true

RUN mkdir -p /logs/verifier

CMD ["/bin/bash"]
