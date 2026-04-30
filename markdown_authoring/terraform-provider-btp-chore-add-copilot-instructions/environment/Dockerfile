FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/terraform-provider-btp && \
    cd /workspace/terraform-provider-btp && \
    git remote add origin https://github.com/SAP/terraform-provider-btp.git && \
    git fetch --depth=1 origin c660459ec6f94cfa36a29ff3f52da1760487bec2 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/terraform-provider-btp
