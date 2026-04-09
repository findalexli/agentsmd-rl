FROM golang:1.23

# Install python3 for pytest runner
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create logs directory
RUN mkdir -p /logs/verifier

# Clone containerd repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=e809b6b8139c1b8afbb081d007ae8ce5858d46a7
RUN git clone --filter=blob:none https://github.com/containerd/containerd.git /workspace/containerd && \
    cd /workspace/containerd && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/containerd
