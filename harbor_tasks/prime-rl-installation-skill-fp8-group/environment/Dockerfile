FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install \
        pytest==8.3.4 \
        pytest-json-report==1.5.0 \
        tomli==2.2.1

WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/PrimeIntellect-ai/prime-rl.git
WORKDIR /workspace/prime-rl
RUN git checkout 7036a1511904cc908b64207ebbd8303053aacf18

RUN mkdir -p /logs/verifier
