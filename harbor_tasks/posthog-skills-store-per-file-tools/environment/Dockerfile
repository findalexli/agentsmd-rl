FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install \
        pytest==8.3.4 \
        pytest-json-report==1.5.0 \
        PyYAML==6.0.2

WORKDIR /workspace

RUN git init /workspace/posthog && \
    cd /workspace/posthog && \
    git remote add origin https://github.com/PostHog/posthog.git && \
    git fetch --depth=1 origin 05e8c588d25b28716a4b64823d5e2b81fde9b6f2 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier
