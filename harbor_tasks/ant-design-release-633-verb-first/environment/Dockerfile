FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    patch \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    pytest==8.3.4 \
    pytest-json-ctrf==0.4.1

WORKDIR /workspace

ARG REPO_SHA=a01bfdf519249a97759a9f13462afc2e3fa0c491
RUN curl -sL "https://codeload.github.com/ant-design/ant-design/tar.gz/${REPO_SHA}" -o /tmp/antd.tar.gz \
    && tar -xzf /tmp/antd.tar.gz \
    && mv "ant-design-${REPO_SHA}" ant-design \
    && rm /tmp/antd.tar.gz

RUN mkdir -p /logs/verifier
