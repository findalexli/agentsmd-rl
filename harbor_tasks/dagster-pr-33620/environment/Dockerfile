FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone the repo at the base commit
RUN git clone --filter=blob:none https://github.com/dagster-io/dagster.git dagster
WORKDIR /workspace/dagster
RUN git checkout 095d02df486d2ab390f8d2385e1ef9413ecf37e0

# Install dependencies needed for testing
RUN pip install --no-cache-dir uv && uv pip install --system \
    pytest \
    pytest-asyncio \
    dlt \
    pendulum \
    pyarrow \
    pandas \
    polars \
    duckdb \
    sqlalchemy \
    pydantic \
    grpcio \
    grpcio-tools

# Install dagster core packages from source (all at once to resolve dev version deps)
RUN uv pip install --system \
    -e python_modules/dagster \
    -e python_modules/dagster-pipes \
    -e python_modules/libraries/dagster-shared \
    -e python_modules/libraries/dagster-dlt \
    dlt \
    pendulum \
    pyarrow \
    pandas \
    polars \
    duckdb \
    sqlalchemy \
    pydantic \
    grpcio \
    grpcio-tools \
    "ruff==0.15.0" \
    --python python3.12

# Create log directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/dagster