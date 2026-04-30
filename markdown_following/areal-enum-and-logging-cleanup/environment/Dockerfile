FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

RUN git init /workspace/AReaL && \
    cd /workspace/AReaL && \
    git remote add origin https://github.com/inclusionAI/AReaL.git && \
    git fetch --depth=1 origin 4f5a2944f0acfebba378e5b88bf2ab940f84b943 && \
    git checkout FETCH_HEAD

# Test/runtime deps. Keep this list tight: types.py needs torch + openai;
# clevr_count_70k.py needs colorlog (via areal/utils/logging.py).
# transformers/numpy/PIL are NOT installed because we patch areal.api at
# import-time with a stub ModelResponse to avoid pulling that subtree in.
RUN pip install --extra-index-url https://download.pytorch.org/whl/cpu \
        pytest==8.3.4 \
        pytest-json-report==1.5.0 \
        torch==2.9.1+cpu \
        openai==2.8.0 \
        colorlog==6.9.0 \
        ruff==0.14.9

RUN mkdir -p /logs/verifier
