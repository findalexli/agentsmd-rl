FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        patch \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.3.7

WORKDIR /workspace

RUN git clone https://github.com/ant-design/ant-design.git antd \
    && cd antd \
    && git -c advice.detachedHead=false checkout 9a3dccf2d4be0f2a271c5a047b7056cf2e429af1

WORKDIR /workspace/antd

RUN mkdir -p /logs/verifier

CMD ["bash"]
