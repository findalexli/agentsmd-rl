FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/clinical-quality-language && \
    cd /workspace/clinical-quality-language && \
    git remote add origin https://github.com/cqframework/clinical_quality_language.git && \
    git fetch --depth=1 origin 344e8274b66baf88e3b0f2c4118ad2fee11b2ceb && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/clinical-quality-language
