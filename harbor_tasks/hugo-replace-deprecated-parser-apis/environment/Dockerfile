FROM golang:1.24-bookworm

# Install Python for test runner
RUN apt-get update && apt-get install -y python3 python3-pip bc && rm -rf /var/lib/apt/lists/*

# Allow Go toolchain to auto-upgrade for modules requiring newer Go
ENV GOTOOLCHAIN=auto

# Set working directory
WORKDIR /workspace

# Clone Hugo repository at base commit (parent of merge commit)
ARG BASE_COMMIT=8b7b6af92c0c01e258b52e1e0658e9f296f74410
RUN git init /workspace/&& && \
    cd /workspace/&& && \
    git remote add origin https://github.com/gohugoio/hugo.git && \
    git fetch --depth=1 origin 8b7b6af92c0c01e258b52e1e0658e9f296f74410 && \
    git checkout FETCH_HEAD

# Install Go dependencies (Hugo doesn't use go.mod in traditional sense for build)
WORKDIR /workspace/hugo

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
