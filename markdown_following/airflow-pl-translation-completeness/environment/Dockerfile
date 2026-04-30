FROM python:3.12.7-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git=1:2.39.* \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install \
        pytest==8.3.4 \
        pytest-json-ctrf==0.3.7

WORKDIR /workspace

ARG BASE_COMMIT=01c404679384d3ca654e44e7243266f508921aac

RUN git clone --filter=blob:none --no-checkout --depth 1 \
        https://github.com/apache/airflow.git /workspace/airflow \
    && cd /workspace/airflow \
    && git fetch --depth 1 origin ${BASE_COMMIT} \
    && git sparse-checkout init --cone \
    && git sparse-checkout set \
        .github/skills \
        airflow-core/src/airflow/ui/public/i18n/locales \
    && git checkout ${BASE_COMMIT} \
    && git config user.email "task@example.com" \
    && git config user.name "Task Runner"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/airflow
