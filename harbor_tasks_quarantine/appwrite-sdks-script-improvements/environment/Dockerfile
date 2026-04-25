FROM php:8.3-cli

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    unzip \
    curl \
    libzip-dev \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install PHP extensions
RUN docker-php-ext-install zip

# Install Composer
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/bin --filename=composer

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Clone the repository at the base commit
ARG BASE_COMMIT=7fcc6406520a04f32d4a61ec147a9e67995d9f8f
RUN git clone --filter=blob:none https://github.com/appwrite/appwrite.git /workspace/appwrite \
    && cd /workspace/appwrite \
    && git checkout ${BASE_COMMIT}

WORKDIR /workspace/appwrite

# Install all PHP dependencies (including dev for testing)
# Using --ignore-platform-reqs since we only need dev tools (pint, phpstan, phpunit)
RUN composer install --no-interaction --prefer-dist --optimize-autoloader --ignore-platform-reqs

# Install pytest for testing
RUN pip3 install pytest --break-system-packages
