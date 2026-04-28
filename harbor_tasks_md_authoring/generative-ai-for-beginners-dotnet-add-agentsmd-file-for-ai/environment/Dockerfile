FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/generative-ai-for-beginners-dotnet && \
    cd /workspace/generative-ai-for-beginners-dotnet && \
    git remote add origin https://github.com/microsoft/Generative-AI-for-beginners-dotnet.git && \
    git fetch --depth=1 origin a94247af01c2568c0f27710d24f0f2fb420b6990 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/generative-ai-for-beginners-dotnet
