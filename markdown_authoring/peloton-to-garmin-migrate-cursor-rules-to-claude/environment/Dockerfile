FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/peloton-to-garmin && \
    cd /workspace/peloton-to-garmin && \
    git remote add origin https://github.com/philosowaffle/peloton-to-garmin.git && \
    git fetch --depth=1 origin 8a474b037792e12cf67fa495c8d617efbeab189e && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/peloton-to-garmin
