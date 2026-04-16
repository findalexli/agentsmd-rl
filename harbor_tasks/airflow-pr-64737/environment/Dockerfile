FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone the repository at the base commit (before the fix)
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/airflow.git airflow \
    && cd airflow \
    && git checkout 7346de5eb65ca9ba66e7d9c5b2ad9413f6b6a2c2

WORKDIR /workspace/airflow

# Install minimal dependencies for testing
RUN pip install --no-cache-dir \
    pytest \
    sqlalchemy>=2.0

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

CMD ["/bin/bash"]
