FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install pytest

RUN mkdir -p /workspace /logs/verifier

# Do a sparse checkout of just the file we need
WORKDIR /workspace
RUN git init ClickHouse && \
    cd ClickHouse && \
    git remote add origin https://github.com/ClickHouse/ClickHouse.git && \
    git config core.sparseCheckout true && \
    echo "src/DataTypes/Serializations/SerializationObject.cpp" > .git/info/sparse-checkout && \
    git fetch --depth=1 origin 7edb784eccbce08cebbec3147591f56d11dd5f9f && \
    git checkout FETCH_HEAD

WORKDIR /workspace/ClickHouse
