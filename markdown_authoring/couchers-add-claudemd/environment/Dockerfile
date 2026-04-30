FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/couchers && \
    cd /workspace/couchers && \
    git remote add origin https://github.com/Couchers-org/couchers.git && \
    git fetch --depth=1 origin 5bdeccbb74f2d674a7ef0f3600c7a4e56056667e && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/couchers
