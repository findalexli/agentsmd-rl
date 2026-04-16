FROM python:3.12-slim

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    make \
    && rm -rf /var/lib/apt/lists/*

# Clone the OpenHands repository at base commit
# Using depth=100 to get enough history for the base commit
RUN git clone --depth=100 --filter=blob:none https://github.com/OpenHands/OpenHands.git /workspace/OpenHands \
    && cd /workspace/OpenHands \
    && git checkout c00f90bf86715dc8ea342efb835f92c74077be02

WORKDIR /workspace/OpenHands

# Install Poetry
RUN pip install poetry

# Configure Poetry to not create virtualenv (install globally)
RUN poetry config virtualenvs.create false

# Install only production dependencies (much faster, no torch/GPU libs)
# We use --no-dev to skip dev dependencies which may include heavy packages
RUN poetry install --no-interaction --no-ansi --no-dev || \
    (echo "Some packages failed, trying with main dependencies only" && \
     poetry install --no-interaction --no-ansi --only main)

# Ensure logs directory exists for test results
RUN mkdir -p /logs/verifier

# Set Python path
ENV PYTHONPATH=/workspace/OpenHands:$PYTHONPATH
