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

RUN git clone --filter=blob:none --no-checkout https://github.com/apache/airflow.git airflow \
    && cd airflow \
    && git checkout e9aa3aa3e57751b77c05d5a66d328e27eae07f7f

RUN pip install --no-cache-dir \
        "apache-airflow==3.2.1" \
        "apache-airflow-providers-common-compat==1.14.3" \
        "opensearch-py==2.7.1" \
        "pytest==8.3.4" \
        "pytest-mock==3.14.0" \
        "pytest-json-report==1.5.0" \
        "ruff==0.13.3"

RUN pip install --no-cache-dir --no-deps -e /workspace/airflow/providers/opensearch

RUN mkdir -p /logs/verifier

WORKDIR /workspace/airflow
