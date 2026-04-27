FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install \
        pytest==8.3.4 \
        ruff==0.14.9

WORKDIR /workspace

ARG AREAL_BASE_COMMIT=9e8b893eccbf92b7ac55942b40f008cc3c615007

RUN git clone --filter=blob:none https://github.com/inclusionAI/AReaL.git areal \
    && cd areal \
    && git checkout ${AREAL_BASE_COMMIT}

WORKDIR /workspace/areal

RUN mkdir -p /logs/verifier
