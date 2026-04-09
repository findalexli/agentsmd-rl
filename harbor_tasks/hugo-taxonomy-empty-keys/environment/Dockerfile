FROM golang:1.24-bookworm

# Install python3 for pytest
RUN apt-get update && apt-get install -y python3 python3-pip git && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create logs directory
RUN mkdir -p /logs/verifier

# Clone Hugo at base commit (with depth for efficiency)
ARG BASE_COMMIT=cc338a9d4854c7e7273a5c3c8fee436c642f4dde
RUN git clone --filter=blob:none --depth=100 https://github.com/gohugoio/hugo.git /workspace/hugo && \
    cd /workspace/hugo && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/hugo
