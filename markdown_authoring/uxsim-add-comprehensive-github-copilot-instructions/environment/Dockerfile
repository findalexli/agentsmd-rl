FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/uxsim && \
    cd /workspace/uxsim && \
    git remote add origin https://github.com/toruseo/UXsim.git && \
    git fetch --depth=1 origin 22ea186bab516bf42af3b7c2112f6a6c988f27f7 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/uxsim
