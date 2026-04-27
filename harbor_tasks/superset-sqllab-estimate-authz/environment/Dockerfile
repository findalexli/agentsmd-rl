FROM python:3.11-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        build-essential \
        pkg-config \
        libpq-dev \
        libssl-dev \
        libsasl2-dev \
        libldap2-dev \
        default-libmysqlclient-dev \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

ARG SUPERSET_REPO=https://github.com/apache/superset.git
ARG SUPERSET_COMMIT=ed3c5280a9340237277156858ea82719e8ba05a5

RUN git clone --filter=blob:none "${SUPERSET_REPO}" superset \
    && cd superset \
    && git checkout "${SUPERSET_COMMIT}"

WORKDIR /workspace/superset

RUN pip install --upgrade pip==24.3.1 setuptools==75.6.0 wheel==0.45.1

RUN pip install -r requirements/base.txt

RUN pip install -e .

RUN pip install \
        pytest==8.3.4 \
        pytest-mock==3.14.0 \
        pytest-asyncio==0.24.0 \
        pytest-json-report==1.5.0

RUN mkdir -p /logs/verifier

ENV PYTHONPATH=/workspace/superset

CMD ["bash"]
