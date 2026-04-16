# Dockerfile for selenium-py-type-stubs task
FROM python:3.12-slim

# Install git and basic tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Clone Selenium repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/SeleniumHQ/selenium.git && \
    cd selenium && \
    git checkout 39436b0c1eabbed5489148b98a36302d77feed9e

# Install Python dependencies for type checking and testing
WORKDIR /workspace/selenium/py
RUN pip install --no-cache-dir \
    mypy>=1.0.0 \
    typing_extensions>=4.0.0 \
    certifi \
    trio \
    trio-websocket \
    urllib3 \
    websocket-client

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/selenium
