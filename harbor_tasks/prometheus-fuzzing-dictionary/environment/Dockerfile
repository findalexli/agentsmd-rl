FROM golang:1.25.0-bookworm

# Install python3 for pytest
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the repo at base commit
ARG BASE_COMMIT=e77e0eb7610db21324631d43a924bb089b1af804
RUN git clone --filter=blob:none https://github.com/prometheus/prometheus.git prometheus && \
    cd prometheus && \
    git checkout ${BASE_COMMIT}

# Create log directory
RUN mkdir -p /logs/verifier

# Set working directory to the repo
WORKDIR /workspace/prometheus
