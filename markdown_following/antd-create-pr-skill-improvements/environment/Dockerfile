FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    pytest==8.3.4 \
    pyyaml==6.0.2

ARG REPO_URL=https://github.com/ant-design/ant-design.git
ARG BASE_COMMIT=3e0031bae868475ce0746651bf70a5a2f705db63

RUN mkdir -p /workspace \
 && git clone --filter=blob:none "$REPO_URL" /workspace/ant-design \
 && cd /workspace/ant-design \
 && git checkout "$BASE_COMMIT"

WORKDIR /workspace/ant-design

RUN mkdir -p /logs/verifier
