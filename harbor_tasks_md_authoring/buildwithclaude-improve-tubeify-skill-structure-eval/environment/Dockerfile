FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/buildwithclaude && \
    cd /workspace/buildwithclaude && \
    git remote add origin https://github.com/davepoon/buildwithclaude.git && \
    git fetch --depth=1 origin 7cc63f3632f01e21f414d2d26241e2965153259a && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/buildwithclaude
