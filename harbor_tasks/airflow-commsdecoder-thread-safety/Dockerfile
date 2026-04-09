FROM python:3.12-slim

WORKDIR /workspace

# Install git and required dependencies
RUN apt-get update && apt-get install -y \
    git \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Clone the repository at base commit
# Using depth=100 to ensure we have enough history but keeping it shallow for speed
RUN git clone --depth=100 https://github.com/apache/airflow.git airflow \
    && cd airflow \
    && git checkout 6fd0142229eab87f23f95e5268aa80db1df8f9f3

# Install uv for dependency management (Airflow uses uv workspaces)
RUN pip install uv

# Set up the task-sdk project environment
# Install only deps needed for the test - msgspec, structlog, pytest
RUN cd /workspace/airflow/task-sdk \
    && uv pip install --system -e . \
    && pip install pytest msgspec structlog

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory for the task
WORKDIR /workspace/airflow
