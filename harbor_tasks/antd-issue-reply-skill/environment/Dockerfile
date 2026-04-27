FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-report==1.5.0 \
        PyYAML==6.0.2

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git \
    && cd ant-design \
    && git checkout b94b29f44b6658fd76cdd70ac49b01c62b6680b2 \
    && git config user.email "task@local" \
    && git config user.name "task"

RUN mkdir -p /logs/verifier
