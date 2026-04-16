FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    make \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone the dagster repo at base commit (shallow clone for speed)
RUN git clone --depth=100 --filter=blob:none https://github.com/dagster-io/dagster.git && \
    cd dagster && \
    git checkout 8628a8c83b62f437bdbc6dfb0baab6698fa1f32d

# Install minimal dependencies for testing
RUN pip install --no-cache-dir \
    pytest \
    pytz \
    croniter \
    ruff==0.15.0

# Install dagster-pipes first (required dependency)
RUN cd /workspace/dagster/python_modules/dagster-pipes && \
    pip install -e .

# Install dagster-shared (required dependency)
RUN cd /workspace/dagster/python_modules/libraries/dagster-shared && \
    pip install -e .

# Install dagster package in editable mode
RUN cd /workspace/dagster/python_modules/dagster && \
    pip install -e .

RUN mkdir -p /logs/verifier

WORKDIR /workspace/dagster
