FROM debian:bookworm-slim

# Install Python, git, and other dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    gcc \
    libc6-dev \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Go 1.23 manually (newer than Debian's package but compatible with most repos)
RUN curl -L https://go.dev/dl/go1.23.5.linux-amd64.tar.gz | tar -C /usr/local -xzf -
ENV PATH=/usr/local/go/bin:$PATH
ENV GOPATH=/go
ENV PATH=$GOPATH/bin:$PATH
RUN mkdir -p "$GOPATH/src" "$GOPATH/bin" && chmod -R 777 "$GOPATH"

# Install pytest
RUN pip3 install pytest --break-system-packages

# Clone Hugo repository at base commit (shallow clone for speed)
ARG BASE_COMMIT=86786c91e597487a0ecc502e6756ebba469f7890
RUN git clone --filter=blob:none https://github.com/gohugoio/hugo.git /workspace/hugo \
    && cd /workspace/hugo \
    && git fetch --depth=1 origin ${BASE_COMMIT} \
    && git checkout ${BASE_COMMIT}

WORKDIR /workspace/hugo

# Install Go dependencies
RUN go mod download

# Install mage
RUN go install github.com/magefile/mage@v1.15.0

# Install staticcheck
RUN go install honnef.co/go/tools/cmd/staticcheck@latest

# Create logs directory
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
