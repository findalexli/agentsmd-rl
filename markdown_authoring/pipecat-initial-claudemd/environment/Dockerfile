FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/pipecat && \
    cd /workspace/pipecat && \
    git remote add origin https://github.com/pipecat-ai/pipecat.git && \
    git fetch --depth=1 origin 2db3d94d06e72c58d35cf67dc22dea9b5e051d94 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/pipecat
