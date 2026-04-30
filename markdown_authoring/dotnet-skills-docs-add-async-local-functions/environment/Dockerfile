FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/dotnet-skills && \
    cd /workspace/dotnet-skills && \
    git remote add origin https://github.com/Aaronontheweb/dotnet-skills.git && \
    git fetch --depth=1 origin 8b83f4978a58f0a81aa181134a0c56c509f8a519 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/dotnet-skills
