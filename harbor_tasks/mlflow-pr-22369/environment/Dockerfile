FROM python:3.12-slim

WORKDIR /workspace

# Install git and curl for fetching
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Clone mlflow at base commit (b3075b40fed52161849b3a238c06d3b36102e0f4)
RUN git clone --filter=blob:none --depth=1 https://github.com/mlflow/mlflow.git

WORKDIR /workspace/mlflow

# Checkout base commit (before the fix)
RUN git fetch --filter=blob:none https://github.com/mlflow/mlflow.git b3075b40fed52161849b3a238c06d3b36102e0f4 && \
    git checkout b3075b40fed52161849b3a238c06d3b36102e0f4

# Install mlflow with tracing extras (needed for the tracing utils module)
RUN pip install --no-cache-dir -e ".[tracing]"

# Install pytest for running tests
RUN pip install --no-cache-dir pytest==8.3.4 pytest-mock==3.14.0

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]