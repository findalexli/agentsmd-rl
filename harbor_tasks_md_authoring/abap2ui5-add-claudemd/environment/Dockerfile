FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/abap2ui5 && \
    cd /workspace/abap2ui5 && \
    git remote add origin https://github.com/abap2UI5/abap2UI5.git && \
    git fetch --depth=1 origin c4e9ac81275a8071006d6152fc2b517415a92c72 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/abap2ui5
