FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv for package management
RUN pip install --no-cache-dir uv

# Clone repository at base commit (before the fix)
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/airflow.git airflow \
    && cd airflow \
    && git checkout 97deef5f615b17f618a2bf4c2e9e0f8c3ec15cde

WORKDIR /workspace/airflow

# Install airflow-core with test dependencies using uv
# We need SQLAlchemy, pytest, and related testing packages
RUN uv pip install --system --no-cache \
    pytest \
    pytest-timeout \
    time-machine \
    pendulum \
    sqlalchemy \
    sqlalchemy-utils \
    alembic

# Install airflow-core package
RUN uv pip install --system --no-cache -e ./airflow-core[dev] || \
    uv pip install --system --no-cache -e ./airflow-core

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set Python path
ENV PYTHONPATH=/workspace/airflow/airflow-core/src

CMD ["/bin/bash"]

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages ruff 2>/dev/null || pip install --no-cache-dir ruff
