FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git \
    && cd ant-design \
    && git checkout 2129ad4461103ec0bbe025cfd8bd26bf4e8b780b

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ant-design
