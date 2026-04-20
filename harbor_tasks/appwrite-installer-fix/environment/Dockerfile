FROM php:8.3-cli

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    unzip \
    curl \
    libssl-dev \
    libbrotli-dev \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install Swoole extension (disable features we don't need)
RUN pecl install swoole-6.0.0 --enable-swoole-curl=no --enable-swoole-pgsql=no && docker-php-ext-enable swoole

# Install Composer
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/bin --filename=composer

# Create logs directory
RUN mkdir -p /logs/verifier

# Clone the repository at base commit
WORKDIR /workspace
ARG BASE_COMMIT=ea032c28046c9f6cb1c2801fa80a9111f7e5fcd1
RUN git clone --filter=blob:none https://github.com/appwrite/appwrite.git appwrite && \
    cd appwrite && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/appwrite

# Install PHP dependencies (skip scripts to avoid pre-install hooks that might fail)
RUN composer install --no-scripts --no-interaction 2>/dev/null || true

# Set up Python environment for tests
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip
