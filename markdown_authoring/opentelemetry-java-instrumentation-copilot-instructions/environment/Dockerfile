FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/opentelemetry-java-instrumentation && \
    cd /workspace/opentelemetry-java-instrumentation && \
    git remote add origin https://github.com/open-telemetry/opentelemetry-java-instrumentation.git && \
    git fetch --depth=1 origin 9bf4a608bac8b8154740114410efd26342140c88 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/opentelemetry-java-instrumentation
