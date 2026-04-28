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
    git fetch --depth=1 origin 38cda561f2a80ef546ff2bdaafc48d06276be22b && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/dotnet-skills
