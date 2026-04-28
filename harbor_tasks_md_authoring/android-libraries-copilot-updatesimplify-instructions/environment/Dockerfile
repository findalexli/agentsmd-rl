FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/android-libraries && \
    cd /workspace/android-libraries && \
    git remote add origin https://github.com/dotnet/android-libraries.git && \
    git fetch --depth=1 origin f0f81d4fe826c549308be9ef5f6d9cea11d05771 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/android-libraries
