FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/dftk.jl && \
    cd /workspace/dftk.jl && \
    git remote add origin https://github.com/JuliaMolSim/DFTK.jl.git && \
    git fetch --depth=1 origin 174fe331f11f9e099ca1a8b321e448e4265e0300 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/dftk.jl
