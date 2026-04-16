FROM php:8.3-cli

# Install dependencies and PHP extensions
RUN apt-get update && apt-get install -y \
    git \
    unzip \
    libssl-dev \
    libcurl4-openssl-dev \
    pkg-config \
    libmongoc-dev \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Swoole extension
RUN pecl install swoole-6.0.2 && docker-php-ext-enable swoole

# Install MongoDB extension
RUN pecl install mongodb && docker-php-ext-enable mongodb

# Install Composer
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

# Set working directory
WORKDIR /workspace

# Clone the repository at base commit (before PR)
ARG BASE_COMMIT=3ed1ca736dd2889b675775687e58db041283ad5a
RUN git clone --filter=blob:none https://github.com/appwrite/appwrite.git && \
    cd appwrite && \
    git checkout ${BASE_COMMIT}

# Install PHP dependencies
WORKDIR /workspace/appwrite
RUN composer install --no-dev --optimize-autoloader --ignore-platform-req=ext-swoole 2>&1 || true

# Install pytest for test runner
RUN pip3 install pytest --break-system-packages

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/appwrite
