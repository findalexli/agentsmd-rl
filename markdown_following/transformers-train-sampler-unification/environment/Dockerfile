FROM python:3.12-slim

WORKDIR /workspace

# Install git, build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Clone the transformers repo at the PR's actual base commit
RUN git clone --filter=blob:none --depth=1 https://github.com/huggingface/transformers.git && \
    cd transformers && \
    git fetch --depth=1 origin e2372ffabdf6da99364d3d053da7783acf5f623c && \
    git checkout e2372ffabdf6da99364d3d053da7783acf5f623c

WORKDIR /workspace/transformers

# Install PyTorch CPU and accelerate (needed for transformers training functionality)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir accelerate

# Install transformers in editable mode
RUN pip install --no-cache-dir pytest && \
    pip install --no-cache-dir -e . --quiet

# Create logs directory for Harbor verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
