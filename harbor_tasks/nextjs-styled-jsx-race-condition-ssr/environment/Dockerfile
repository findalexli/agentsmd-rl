FROM python:3.11-slim

WORKDIR /workspace/taskforge

# Install dependencies
RUN pip install --no-cache-dir pydantic pyyaml

# Copy the taskforge package
COPY taskforge/ ./taskforge/

# Set Python path
ENV PYTHONPATH=/workspace/taskforge:$PYTHONPATH

WORKDIR /workspace/taskforge
