# syntax=docker/dockerfile:1.4
FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux \
        python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (large monorepo — use blob filter)
RUN git init /workspace/supabase && \
    cd /workspace/supabase && \
    git remote add origin https://github.com/supabase/supabase.git && \
    git fetch --depth=1 origin 11d4da6c4b6d282c1d829a4786a342468472a698 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/supabase

# Normalize curly/smart quotes to ASCII in RULE.md so the gold patch applies
# (the file uses U+2019 right single quotes but the patch expects ASCII apostrophes)
# NOTE: arrows (U+2192) are left alone — the patch expects them unchanged
COPY <<'EOF' /tmp/normalize_quotes.py
text = open('.cursor/rules/studio/queries/RULE.md', 'rb').read()
text = text.replace(b'\xe2\x80\x99', b'\x27')   # U+2019 right single quote -> '
text = text.replace(b'\xe2\x80\x98', b'\x27')   # U+2018 left single quote -> '
text = text.replace(b'\xe2\x80\x9c', b'\x22')   # U+201C left double quote -> "
text = text.replace(b'\xe2\x80\x9d', b'\x22')   # U+201D right double quote -> "
open('.cursor/rules/studio/queries/RULE.md', 'wb').write(text)
print('Curly quotes normalized.')
EOF
RUN python3 /tmp/normalize_quotes.py

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier