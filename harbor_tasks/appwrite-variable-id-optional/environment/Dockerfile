FROM php:8.3-cli

# Install Python3 and pip for pytest
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create workspace directory
WORKDIR /workspace

# Clone appwrite repo at base commit (before fix)
RUN git clone --filter=blob:none https://github.com/appwrite/appwrite.git && \
    cd appwrite && \
    git checkout 20f80ac067e0042ea05ac9566f0a9ff1624bf3b2

# Create log directory for verifier
RUN mkdir -p /logs/verifier

# Copy test files
COPY tests/test_outputs.py /workspace/test_outputs.py

# Default command runs tests
CMD ["bash", "/workspace/test.sh"]
