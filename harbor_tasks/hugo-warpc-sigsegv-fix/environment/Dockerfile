FROM golang:1.25-bookworm

# Install Python for pytest test runner and patch for applying fixes
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

WORKDIR /workspace

# Clone Hugo repo at base commit (parent of merge commit)
ARG BASE_COMMIT=54c804876a5b63c3447b612ce6823339f3f486fc
RUN git clone --filter=blob:none --depth=1 https://github.com/gohugoio/hugo.git && \
    cd hugo && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Pre-download Go module dependencies to speed up builds
RUN cd hugo && go mod download

# Create log directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/hugo
RUN mkdir -p /workspace/task && ln -s /tests /workspace/task/tests
