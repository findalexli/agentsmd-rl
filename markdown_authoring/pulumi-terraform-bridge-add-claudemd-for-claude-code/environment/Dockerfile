FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/pulumi-terraform-bridge && \
    cd /workspace/pulumi-terraform-bridge && \
    git remote add origin https://github.com/pulumi/pulumi-terraform-bridge.git && \
    git fetch --depth=1 origin 961efe5cf602c78d021d1509b40d557bf8af5c59 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/pulumi-terraform-bridge
