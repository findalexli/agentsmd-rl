FROM python:3.12-slim

# Install git and other dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster Python package management
RUN pip install uv

# Clone the repository at the base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/airflow.git airflow && \
    cd airflow && \
    git checkout 9e2bf8110b4d273ff93c9dccc9023188cdf51af0

# Install pytest for the test harness
RUN pip install pytest

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/airflow
