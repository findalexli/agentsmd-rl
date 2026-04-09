FROM php:8.3-cli

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    unzip \
    curl \
    libonig-dev \
    libzip-dev \
    libxml2-dev \
    && rm -rf /var/lib/apt/lists/*

# Install PHP extensions
RUN docker-php-ext-install \
    mbstring \
    zip \
    xml

# Install Composer
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

# Install Python (needed by test runner)
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*

# Clone the repository at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/appwrite/appwrite.git && \
    cd appwrite && \
    git checkout 951a96ae01bceaabe6e2fb936686b7953209ce19

# Install PHP dependencies (composer install)
WORKDIR /workspace/appwrite
RUN composer install --no-interaction --prefer-dist --optimize-autoloader 2>/dev/null || true

# Setup logging directory
RUN mkdir -p /logs/verifier

# Copy test script
COPY tests/test_outputs.py /workspace/test_outputs.py
COPY tests/test.sh /workspace/test.sh
RUN chmod +x /workspace/test.sh

WORKDIR /workspace
