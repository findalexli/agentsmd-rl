FROM python:3.11-slim

# Install system dependencies for matplotlib build and tests
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libcairo2-dev \
    libffi-dev \
    libfreetype6-dev \
    libgeos-dev \
    libpng-dev \
    ninja-build \
    pkg-config \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python build dependencies first
RUN pip install --no-cache-dir \
    meson-python \
    pybind11 \
    numpy \
    setuptools-scm

# Install runtime and test dependencies
RUN pip install --no-cache-dir \
    pillow \
    contourpy \
    cycler \
    fonttools \
    kiwisolver \
    packaging \
    pyparsing \
    python-dateutil \
    pytest \
    pytest-xdist \
    pytest-timeout \
    pytest-cov \
    ruff \
    build

# Clone matplotlib at a specific commit (shallow clone for speed)
WORKDIR /workspace
RUN git clone --depth 100 --branch main https://github.com/matplotlib/matplotlib.git matplotlib

WORKDIR /workspace/matplotlib

# Checkout the base commit for this task
RUN git checkout ea362ab57e926a5c88a3b53636c1f8d669b2aa02

# Install matplotlib in editable mode
RUN pip install --no-build-isolation --editable ".[dev]" || \
    pip install --no-build-isolation --editable .

# Create test output directory
RUN mkdir -p /logs/verifier

# Set matplotlib backend to non-interactive Agg for testing
ENV MPLBACKEND=Agg
ENV PYTHONDONTWRITEBYTECODE=1

# The REPO path for test_outputs.py (Docker-internal path)
ENV REPO=/workspace/matplotlib
