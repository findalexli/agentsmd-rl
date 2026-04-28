FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/cvxpy && \
    cd /workspace/cvxpy && \
    git remote add origin https://github.com/cvxpy/cvxpy.git && \
    git fetch --depth=1 origin 266425231bbbe5931f3120abbd8125d17ae0be73 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/cvxpy
