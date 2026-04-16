# Benchmark task environment for apache/airflow#64774
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Clone the repository (sparse checkout for efficiency)
RUN git clone --filter=blob:none https://github.com/apache/airflow.git /workspace/airflow

WORKDIR /workspace/airflow

# Checkout the base commit (parent of merge commit)
RUN git checkout b875c406e62fb7319f0a19f02435d0f54266a9d2

# Install minimal dependencies for testing the script
RUN pip install --no-cache-dir rich click pytest

# Create logs directory
RUN mkdir -p /logs/verifier

# Set up PYTHONPATH for the scripts
ENV PYTHONPATH=/workspace/airflow/scripts/in_container

CMD ["/bin/bash"]
