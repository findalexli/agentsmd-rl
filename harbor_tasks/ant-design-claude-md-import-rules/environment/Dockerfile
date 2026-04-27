FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.3.6

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git ant-design \
 && cd ant-design \
 && git checkout 1f41cc73e855b332d81fc52cd84f1dddad6676a6

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ant-design
