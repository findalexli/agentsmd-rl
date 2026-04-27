FROM php:8.3.15-cli-bookworm

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        unzip \
        ca-certificates \
        python3 \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Composer (pinned)
RUN curl -fsSL https://getcomposer.org/download/2.8.4/composer.phar -o /usr/local/bin/composer \
    && chmod +x /usr/local/bin/composer \
    && composer --version

# Python packages for the harness
RUN pip3 install --break-system-packages --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1 \
        pyyaml==6.0.2

# Clone Appwrite at base commit
RUN git clone --filter=blob:none https://github.com/appwrite/appwrite.git /workspace/appwrite \
    && cd /workspace/appwrite \
    && git checkout ea032c28046c9f6cb1c2801fa80a9111f7e5fcd1

WORKDIR /workspace/appwrite

# Install only the autoloader (no platform-req checks: Swoole etc. not needed for reflection)
RUN composer install --ignore-platform-reqs --no-dev --no-scripts --no-plugins \
        --optimize-autoloader --no-interaction --prefer-dist \
    && rm -rf /root/.composer/cache

RUN mkdir -p /logs/verifier
