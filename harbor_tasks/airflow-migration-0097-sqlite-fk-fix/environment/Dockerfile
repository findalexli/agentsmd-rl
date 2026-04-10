FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the repository at the base commit (shallow clone with only the commit we need)
# Clone to 'task' directory to match expected test paths
RUN git clone --filter=blob:none https://github.com/apache/airflow.git task && \
    cd task && \
    git fetch --depth=1 origin 06101dc5daa2f4a3e4b6020b6e2f305566816e8a && \
    git checkout 06101dc5daa2f4a3e4b6020b6e2f305566816e8a

# Install Python dependencies needed for testing
RUN pip install --no-cache-dir pytest sqlalchemy alembic

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/task
