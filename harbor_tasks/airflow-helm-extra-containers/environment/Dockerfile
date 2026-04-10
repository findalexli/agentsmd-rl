FROM python:3.12-slim

RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*
RUN curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
RUN pip install --no-cache-dir pytest pyyaml jmespath jsonschema
RUN git clone https://github.com/apache/airflow.git /workspace/airflow && cd /workspace/airflow && git checkout 27258d567887a93f43af25a9d79d773198751bd9
RUN mkdir -p /logs/verifier
WORKDIR /workspace/airflow
