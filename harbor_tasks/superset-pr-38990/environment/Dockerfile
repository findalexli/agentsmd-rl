FROM python:3.12-slim

# Install git and dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create workspace
WORKDIR /workspace

# Clone superset repo at the base commit (shallow clone for speed)
RUN git clone --filter=blob:none https://github.com/apache/superset.git superset && \
    cd superset && \
    git checkout 1bb41a6e609320dd2932f67d8373cb7866230f65

# Install Python dependencies for the MCP service (minimal)
RUN pip install --no-cache-dir \
    pydantic \
    pydantic-core

# Create logs directory
RUN mkdir -p /logs/verifier

# Copy test files
COPY tests/test_outputs.py /workspace/tests/
COPY solution/solve.sh /workspace/solution/
RUN chmod +x /workspace/solution/solve.sh
