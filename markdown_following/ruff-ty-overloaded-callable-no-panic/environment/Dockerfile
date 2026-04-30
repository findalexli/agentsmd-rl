FROM rust:1.94-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    CARGO_HOME=/usr/local/cargo \
    RUSTUP_HOME=/usr/local/rustup \
    PATH=/usr/local/cargo/bin:/usr/local/rustup/bin:/usr/local/bin:/usr/bin:/bin \
    CARGO_TERM_COLOR=never \
    CARGO_INCREMENTAL=0 \
    CARGO_PROFILE_DEV_OPT_LEVEL=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        build-essential \
        pkg-config \
        cmake \
        libssl-dev \
        curl \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install pinned pytest + plugins via venv to avoid PEP 668 friction
RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1 \
    && ln -sf /opt/venv/bin/pytest /usr/local/bin/pytest \
    && ln -sf /opt/venv/bin/python /usr/local/bin/python

# Install pinned cargo-nextest
RUN curl -L --proto '=https' --tlsv1.2 -sSf \
        https://get.nexte.st/0.9.88/linux \
        | tar zxf - -C /usr/local/cargo/bin

# Clone ruff at the base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/astral-sh/ruff.git ruff \
    && cd ruff \
    && git checkout 61f9a0a5763fb068cd2f26c0ee9d63a277fb26c2 \
    && git config user.email task@example.com \
    && git config user.name task

WORKDIR /workspace/ruff

# Pre-fetch all dependencies and pre-compile the mdtest target so the
# agent's edit-rebuild loop is fast (only builder.rs needs recompiling).
RUN cargo fetch --locked
RUN cargo nextest --version \
    && CARGO_PROFILE_DEV_OPT_LEVEL=1 \
       cargo nextest list \
        -p ty_python_semantic \
        --test mdtest \
        --locked \
        > /dev/null \
    && rm -rf /workspace/ruff/target/debug/incremental

RUN mkdir -p /logs/verifier
