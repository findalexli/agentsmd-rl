FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/kubectl-operator && \
    cd /workspace/kubectl-operator && \
    git remote add origin https://github.com/operator-framework/kubectl-operator.git && \
    git fetch --depth=1 origin 882354ccd775fffcd9d8b4c122a5e6980f80d223 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/kubectl-operator
