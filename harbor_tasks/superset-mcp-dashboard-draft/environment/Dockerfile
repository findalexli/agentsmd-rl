FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y     git     curl     && rm -rf /var/lib/apt/lists/*

# Create workspace and logs directories
RUN mkdir -p /workspace/superset /logs/verifier

# Clone the repository at the base commit (before the fix)
WORKDIR /workspace
ARG BASE_COMMIT=25eea295f6c9e8060619beccb267dd9c7628f882
RUN git clone --filter=blob:none https://github.com/apache/superset.git &&     cd superset &&     git checkout ${BASE_COMMIT}

# Install Python dependencies for testing
# Install comprehensive deps since superset has many imports
WORKDIR /workspace/superset
RUN pip install --no-cache-dir     pytest     pytest-asyncio     pydantic     pydantic-settings     flask     sqlalchemy     marshmallow     alembic     pandas     numpy     aiohttp     mcp     typing-extensions     celery     redis     click     wtforms

# Set up entrypoint
WORKDIR /workspace/superset
