FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        patch \
        grep \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git \
    && cd ant-design \
    && git checkout 90d22892c1f88b46d46593157321a1f05e5c1ed2 \
    && git config user.email scaffold@example.com \
    && git config user.name scaffold

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ant-design
