FROM rust:1.95-slim

RUN apt-get update && apt-get install -y \
    python3 \
    python3-venv \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/astral-sh/ruff.git ruff && \
    cd ruff && \
    git checkout d3ef4e210d72fac3f1b6a5c59f483648904c12ed

WORKDIR /workspace/ruff

RUN cargo fetch
RUN cargo check -p ty_python_semantic

RUN pip install pytest==8.3.4

RUN mkdir -p /logs/verifier
