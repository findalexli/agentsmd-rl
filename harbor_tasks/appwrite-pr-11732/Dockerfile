FROM php:8.3-cli-slim

# Install git and dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Create logs directory
RUN mkdir -p /logs/verifier

# Clone the repository at base commit
ARG REPO_SHORT=appwrite
ARG BASE_COMMIT=3ed1ca736dd2889b675775687e58db041283ad5a
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/appwrite/appwrite.git ${REPO_SHORT}
WORKDIR /workspace/${REPO_SHORT}
RUN git checkout ${BASE_COMMIT}

# Set up Python environment for tests
WORKDIR /workspace
RUN python3 -m venv /workspace/.venv
ENV PATH="/workspace/.venv/bin:$PATH"
RUN pip install --upgrade pip pytest pyyaml

# Copy test files
COPY tests/test_outputs.py /workspace/tests/
COPY tests/test.sh /workspace/tests/
COPY solution/solve.sh /workspace/solution/

WORKDIR /workspace
