FROM python:3.12-slim

# Install minimal dependencies (curl for downloading files)
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest

# Create workspace structure
WORKDIR /workspace/ClickHouse
RUN mkdir -p src/Functions tests/queries/0_stateless

# Download only the specific file we need at base commit
RUN curl -sL "https://raw.githubusercontent.com/ClickHouse/ClickHouse/73ad233a01a81190b2a45b820878e54c36a9a22c/src/Functions/padString.cpp" -o src/Functions/padString.cpp

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/ClickHouse
