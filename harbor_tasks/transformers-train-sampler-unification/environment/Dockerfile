FROM python:3.12-slim

WORKDIR /workspace

# Install git and basic build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Clone the transformers repo at base commit
RUN git init /workspace/&& && \
    cd /workspace/&& && \
    git remote add origin https://github.com/huggingface/transformers.git && \
    git fetch --depth=1 origin 8efd81513f51cd343d086e0e8f69190caa49dbcf && \
    git checkout FETCH_HEAD

WORKDIR /workspace/transformers

# Install only minimal dependencies needed for testing (no torch needed for basic syntax/import tests)
RUN pip install --no-cache-dir pytest && \
    pip install --no-cache-dir -e . --quiet

# Create logs directory for Harbor verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
