FROM python:3.12-slim

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Clone the prefect repo at base commit (full checkout)
RUN git clone --depth=1 https://github.com/prefecthq/prefect.git /workspace/prefect_tmp \
    && cd /workspace/prefect_tmp \
    && git fetch --depth=1 origin 42ae6fde9c76e1f5cf40f1449226659319d4220b \
    && git checkout 42ae6fde9c76e1f5cf40f1449226659319d4220b \
    && mv /workspace/prefect_tmp /workspace/prefect

WORKDIR /workspace/prefect

# Install build dependencies
RUN pip install --no-cache-dir hatchling versioningit

# Create necessary module files for prefect
RUN echo '__version__ = "3.0.0"' > src/prefect/_version.py \
    && echo '__sha__ = "42ae6fde9c76e1f5cf40f1449226659319d4220b"' >> src/prefect/_version.py

# Create _build_info.py with all required attributes
RUN echo '__version__ = "3.0.0"' > src/prefect/_build_info.py \
    && echo '__build_date__ = "2025-04-01T00:00:00"' >> src/prefect/_build_info.py \
    && echo '__git_commit__ = "42ae6fde9c76e1f5cf40f1449226659319d4220b"' >> src/prefect/_build_info.py \
    && echo '__dirty__ = False' >> src/prefect/_build_info.py

# Install dependencies without prefect itself
RUN pip install --no-cache-dir \
    pytest pytest-asyncio pytest-mock anyio \
    pydantic pydantic-settings typing_extensions \
    orjson httpx rich toml pyyaml python-dateutil \
    aiosqlite 'sqlalchemy[asyncio]' alembic jinja2 \
    jsonschema cryptography pendulum ruff \
    fastapi uvicorn griffe \
    asyncpg apprise cachetools cloudpickle \
    coolname exceptiongroup fsspec graphviz \
    httpcore humanize jsonpatch opentelemetry-api \
    packaging pathspec pluggy prometheus-client \
    pydantic_core pydantic_extra_types \
    python-slugify pytz readchar rfc3339-validator \
    ruamel.yaml semver sniffio whenever \
    respx mock websockets typing-inspection \
    webservices python-dateutil starlette asgi-lifespan

# Set PYTHONPATH to include src
ENV PYTHONPATH="/workspace/prefect/src:${PYTHONPATH}"

# Create logs directory for verifier
RUN mkdir -p /logs/verifier
