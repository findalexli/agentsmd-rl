FROM python:3.12-slim

# Install git and build dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the repo at base commit
RUN git clone --filter=blob:none https://github.com/dagster-io/dagster.git /workspace/dagster && \
    cd /workspace/dagster && \
    git checkout f44352a8a384296e999c33df60bb785bd69953c4

# Install test dependencies and package requirements
RUN pip install \
    pytest \
    pyright \
    typing_extensions \
    pyyaml \
    pydantic \
    click \
    rich \
    sqlalchemy \
    alembic \
    protobuf \
    grpcio \
    pytz \
    croniter \
    toposort \
    psutil \
    watchdog \
    python-dateutil \
    packaging \
    fsspec \
    universal_pathlib \
    tzdata \
    markupsafe \
    jinja2 \
    tabulate \
    tqdm \
    nodeenv \
    filelock \
    coloredlogs \
    uvicorn \
    starlette \
    nanoid \
    orjson \
    structlog \
    tomli \
    pep562

# Add the dagster packages to PYTHONPATH directly
ENV PYTHONPATH="/workspace/dagster/python_modules/dagster:/workspace/dagster/python_modules/libraries/dagster-shared:/workspace/dagster/python_modules/libraries/dagster-components:/workspace/dagster/python_modules/libraries/dagster-dbt:/workspace/dagster/python_modules/libraries/dagster-pipes"

# Create logs directory
RUN mkdir -p /logs/verifier

# Set final working directory
WORKDIR /workspace/dagster

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages ruff 2>/dev/null || pip install --no-cache-dir ruff
