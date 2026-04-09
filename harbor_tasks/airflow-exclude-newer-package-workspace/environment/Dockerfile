FROM python:3.12-slim

# Install required packages including git and tomllib support
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Install uv for Python package management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Install ruff for linting/formatting checks
RUN pip install ruff

# Create workspace directory
WORKDIR /workspace

# Clone the airflow repository at base commit (shallow clone for speed)
ARG BASE_COMMIT=fc315f3d77f4029c469ebc7d8be35983edcbfc27
RUN git clone --filter=blob:none --depth=100 https://github.com/apache/airflow.git airflow && \
    cd airflow && \
    git fetch --depth=100 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/airflow

# Create logs directory for verifier
RUN mkdir -p /logs/verifier
