FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install \
        pydantic==2.9.2 \
        loguru==0.7.3 \
        pytest==8.3.4 \
        pytest-json-report==1.5.0 \
        numpy==2.2.6 \
        pandas==2.2.3 \
        git+https://github.com/samsja/pydantic_config.git@73c1d84

WORKDIR /workspace

RUN git init /workspace/prime-rl && \
    cd /workspace/prime-rl && \
    git remote add origin https://github.com/PrimeIntellect-ai/prime-rl.git && \
    git fetch --depth=1 origin ecf1ae22746d1a956e666d2c5675a9ac1882490f && \
    git checkout FETCH_HEAD

# Stub transformers.modeling_flash_attention_utils so prime_rl._compat shim
# can run without the real (heavy) transformers / torch deps.
RUN mkdir -p /opt/stubs/transformers \
    && printf '%s\n' 'class _StubModule: pass' > /opt/stubs/transformers/__init__.py \
    && printf '%s\n' 'def is_flash_attn_greater_or_equal_2_10(): return True' \
        > /opt/stubs/transformers/modeling_flash_attention_utils.py

ENV PYTHONPATH=/workspace/prime-rl/src:/opt/stubs

RUN mkdir -p /logs/verifier

WORKDIR /workspace/prime-rl
