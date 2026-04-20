FROM php:8.3-cli

# Install system dependencies and Python
RUN apt-get update && apt-get install -y \
    git \
    unzip \
    curl \
    python3 \
    python3-pip \
    python3-venv \
    libzip-dev \
    libonig-dev \
    libxml2-dev \
    && rm -rf /var/lib/apt/lists/*

# Install PHP extensions
RUN docker-php-ext-install zip mbstring xml

# Install Composer
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/bin --filename=composer

# Set up Python environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip pytest pyyaml

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace

# Clone the appwrite repository at base commit
RUN git clone --filter=blob:none https://github.com/appwrite/appwrite.git && \
    cd appwrite && \
    git checkout bb078086618f85634763943b9bee5fb8e8453cbd

RUN mkdir -p /workspace/task/appwrite-audit-user-types && ln -s /tests /workspace/task/appwrite-audit-user-types/tests

WORKDIR /workspace/appwrite

# Install PHP dependencies (composer install)
RUN composer install --no-interaction --optimize-autoloader --ignore-platform-reqs || true

# Verify PHP and PHPUnit are available
RUN php --version && \
    ls -la vendor/bin/ 2>/dev/null || true
