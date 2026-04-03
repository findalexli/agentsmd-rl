FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (shallow — large Go monorepo)
RUN git init /workspace/dagger && \
    cd /workspace/dagger && \
    git remote add origin https://github.com/dagger/dagger.git && \
    git fetch --depth=1 origin 267017813dfa4a570c29b516288eef01b6fcf100 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/dagger

RUN mkdir -p /logs/verifier
