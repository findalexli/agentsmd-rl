FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

# git: needed to clone the repo and apply the gold patch in solve.sh.
# ca-certificates: TLS roots for git over HTTPS during the clone step only;
#   the script the agent writes will not perform network at test time.
RUN apt-get update && apt-get install -y --no-install-recommends \
        git=1:2.* \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Pinned pytest stack — unpinned versions cause reward noise when upstream bumps a minor.
RUN pip install \
        pytest==8.3.4 \
        pytest-json-ctrf==0.3.5

WORKDIR /workspace

# Shallow checkout at the PR's parent commit. mlflow is a large repo, so we use
# blob:none + sparse fetch by SHA to keep the image small while still giving a
# real working tree (needed because the gold patch references real existing
# context lines in .pre-commit-config.yaml and .github/workflows/lint.yml).
ARG BASE_COMMIT=f79675735e964e14a190186efeb20176b2fe9216
RUN git clone --filter=blob:none https://github.com/mlflow/mlflow.git /workspace/mlflow \
    && cd /workspace/mlflow \
    && git checkout "${BASE_COMMIT}" \
    && git config user.email "task@example.com" \
    && git config user.name "Task Runner"

RUN mkdir -p /logs/verifier
