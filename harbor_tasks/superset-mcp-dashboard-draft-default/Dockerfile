FROM python:3.12-slim

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

RUN pip install pytest pydantic

RUN mkdir -p /workspace/superset && mkdir -p /logs/verifier

RUN git clone --filter=blob:none https://github.com/apache/superset.git /workspace/superset && \
    cd /workspace/superset && \
    git checkout 25eea295f6c9e8060619beccb267dd9c7628f882

WORKDIR /workspace
