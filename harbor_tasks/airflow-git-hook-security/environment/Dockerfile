FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone the airflow repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/airflow.git airflow && \
    cd airflow && \
    git checkout b5dae4e72df868004b53006bb995256ef88d9c0b

# Install the git provider dependencies
WORKDIR /workspace/airflow/providers/git
RUN pip install -e .

# Install pytest for test runner
RUN pip install pytest

# Ensure logs directory exists
RUN mkdir -p /logs/verifier
