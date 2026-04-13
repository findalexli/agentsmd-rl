FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast package management (used by gradio)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Set working directory - this is where the repo lives INSIDE the container
WORKDIR /workspace/gradio

# Clone the repo at the base commit
RUN git clone --depth 1 https://github.com/gradio-app/gradio.git /workspace/gradio

# Install Python dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-xdist \
    ruff \
    mypy \
    build \
    hatchling \
    hatch-requirements-txt \
    hatch-fancy-pypi-readme

# Install gradio and its client in editable mode
RUN pip install -e /workspace/gradio/client/python && \
    pip install -e /workspace/gradio

# Install additional test dependencies
RUN pip install --no-cache-dir \
    pydantic \
    fastapi \
    numpy \
    pillow \
    aiohttp \
    websockets \
    httpx

# Set environment variables
ENV GRADIO_ANALYTICS_ENABLED=False
ENV PYTHONPATH=/workspace/gradio:$PYTHONPATH

# Default command
CMD ["bash"]
