FROM python:3.12.7-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install \
        pytest==8.4.2 \
        pytest-asyncio==1.2.0 \
        grpcio==1.68.1 \
        protobuf==4.25.5 \
        semver==3.0.2 \
        dill==0.4.0 \
        pyyaml==6.0.2 \
        debugpy==1.8.7 \
        packaging==26.0 \
        opentelemetry-api==1.27.0 \
        opentelemetry-sdk==1.27.0 \
        opentelemetry-exporter-otlp-proto-grpc==1.27.0 \
        opentelemetry-instrumentation-grpc==0.48b0

WORKDIR /workspace
RUN git init /workspace/pulumi && \
    cd /workspace/pulumi && \
    git remote add origin https://github.com/pulumi/pulumi.git && \
    git fetch --depth=1 origin b4e628b5434052005d91f9f66fd3ae6dfdf065c5 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/pulumi
ENV PYTHONPATH=/workspace/pulumi/sdk/python/lib

RUN mkdir -p /logs/verifier
