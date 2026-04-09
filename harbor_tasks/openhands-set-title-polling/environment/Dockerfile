FROM python:3.12-slim

# Install git and other dependencies
RUN apt-get update && apt-get install -y \
    git \
    make \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install poetry

# Clone the OpenHands repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/All-Hands-AI/OpenHands.git && \
    cd OpenHands && \
    git checkout eb189144f2dfbbf0dad964cf7bdbd44e7910cb29

WORKDIR /workspace/OpenHands

# Install dependencies (without installing the package itself)
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --with dev || \
    poetry install --no-interaction --no-ansi

# Create logs directory
RUN mkdir -p /logs/verifier

# Default command
CMD ["/bin/bash"]
