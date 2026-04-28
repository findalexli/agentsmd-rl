FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/msbuild.sdk.sqlproj && \
    cd /workspace/msbuild.sdk.sqlproj && \
    git remote add origin https://github.com/rr-wfm/MSBuild.Sdk.SqlProj.git && \
    git fetch --depth=1 origin f066303fa89c701dc00a5b1c3ce80062e3c5df88 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/msbuild.sdk.sqlproj
