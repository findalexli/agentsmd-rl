FROM golang:1.25.0-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV GOFLAGS=-mod=mod
ENV GOTOOLCHAIN=local

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
        bc \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"
RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1

WORKDIR /workspace

RUN git init /workspace/hugo && \
    cd /workspace/hugo && \
    git remote add origin https://github.com/gohugoio/hugo.git && \
    git fetch --depth=1 origin b55d452e46e81369a65978459a0683efa484c11b && \
    git checkout FETCH_HEAD

WORKDIR /workspace/hugo

RUN go mod download

RUN go build -o /tmp/hugo-build . && rm /tmp/hugo-build

RUN go install honnef.co/go/tools/cmd/staticcheck@2025.1.1

ENV PATH="/root/go/bin:${PATH}"

RUN mkdir -p /logs/verifier

CMD ["/bin/bash"]
