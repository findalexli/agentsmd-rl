FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/dbt-databricks && \
    cd /workspace/dbt-databricks && \
    git remote add origin https://github.com/databricks/dbt-databricks.git && \
    git fetch --depth=1 origin affbd61f3eefdef9334993fb7cf557ed1ef54806 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/dbt-databricks
