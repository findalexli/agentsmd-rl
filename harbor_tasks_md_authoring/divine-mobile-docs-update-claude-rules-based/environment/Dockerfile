FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/divine-mobile && \
    cd /workspace/divine-mobile && \
    git remote add origin https://github.com/divinevideo/divine-mobile.git && \
    git fetch --depth=1 origin 2015cbd187de73c4b73d8137469d32ec65e83ba3 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/divine-mobile
