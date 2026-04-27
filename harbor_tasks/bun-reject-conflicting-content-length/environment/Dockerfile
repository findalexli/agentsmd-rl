FROM gcc:13-bookworm

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        git \
        python3 \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --break-system-packages \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1

ENV BUN_REPO=/workspace/bun
ENV BASE_COMMIT=5b3ca83b84f90ccc9c71005db0ab9bd87850bc70

RUN git init -q "$BUN_REPO" \
    && cd "$BUN_REPO" \
    && git config core.sparseCheckout true \
    && mkdir -p .git/info \
    && printf "packages/bun-uws/src/\n" > .git/info/sparse-checkout \
    && git remote add origin https://github.com/oven-sh/bun.git \
    && git fetch --depth 1 origin "$BASE_COMMIT" \
    && git checkout FETCH_HEAD

WORKDIR /workspace/bun

RUN mkdir -p /logs/verifier
