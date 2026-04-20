FROM node:22-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --break-system-packages pytest==8.3.4 pytest-timeout==2.3.1

WORKDIR /workspace

# Clone supabase repo (shallow)
RUN git clone --filter=blob:none --depth=1 https://github.com/supabase/supabase.git supabase-project

WORKDIR /workspace/supabase-project

# Checkout the base commit
RUN git checkout 82deff37de71922332d1b0ca72fb16f3b720ae75

# Install pnpm dependencies
RUN npm install -g pnpm@10 && pnpm install --frozen-lockfile

# Install Studio deps
RUN pnpm install --filter=@supabase/studio

RUN mkdir -p /logs/verifier

ENV PYTHONPATH=/workspace/supabase-project/apps/studio