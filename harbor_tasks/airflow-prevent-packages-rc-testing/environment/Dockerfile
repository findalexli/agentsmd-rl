FROM python:3.12-slim

# Install git, curl, and other dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Clone the repository at base commit
WORKDIR /workspace
ARG REPO_URL=https://github.com/apache/airflow.git
ARG BASE_COMMIT=9e2bf8110b4d273ff93c9dccc9023188cdf51af0
RUN git clone --filter=blob:none --depth=50 ${REPO_URL} airflow
WORKDIR /workspace/airflow
RUN git checkout ${BASE_COMMIT}

# Install pytest for the test runner
RUN pip install --no-cache-dir pytest

# Set working directory for task execution
WORKDIR /workspace/airflow
