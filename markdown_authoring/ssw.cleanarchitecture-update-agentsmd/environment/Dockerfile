FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/ssw.cleanarchitecture && \
    cd /workspace/ssw.cleanarchitecture && \
    git remote add origin https://github.com/SSWConsulting/SSW.CleanArchitecture.git && \
    git fetch --depth=1 origin b0f44ac94d139d73ebaf6af8f03312e6f1ebc079 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ssw.cleanarchitecture
