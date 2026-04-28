FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/mudblazor && \
    cd /workspace/mudblazor && \
    git remote add origin https://github.com/MudBlazor/MudBlazor.git && \
    git fetch --depth=1 origin b0319b7b84975ee4440723f128a92cd678c04778 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/mudblazor
