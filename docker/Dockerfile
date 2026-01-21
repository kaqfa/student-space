# Passenger + Apache Docker Environment
# Simulates Domainesia cPanel + Passenger setup for local testing

FROM phusion/passenger-customizable:3.0.5

# Set maintainer
LABEL maintainer="student-space"
LABEL description="Local Passenger testing environment for Student Space"

# Enable Passenger + Apache
RUN /pd_build/python.sh && \
    /pd_build/utilities.sh

# Install Python 3.12 (match Domainesia version)
RUN apt-get update && \
    apt-get install -y \
        python3.12 \
        python3.12-dev \
        python3.12-venv \
        python3-pip \
        libpq-dev \
        postgresql-client \
        netcat-openbsd \
        vim \
        curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Create virtualenv in similar location as cPanel
RUN python3.12 -m venv /var/www/venv
ENV PATH="/var/www/venv/bin:$PATH"

# Upgrade pip
RUN pip install --upgrade pip setuptools wheel

# Set working directory (simulate GitHub clone location)
WORKDIR /var/www/student-space

# Copy requirements first (Docker layer caching)
COPY requirements/ ./requirements/
RUN pip install --no-cache-dir -r requirements/production.txt && \
    pip install --no-cache-dir python-dotenv

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p \
    /var/www/student-space/staticfiles \
    /var/www/student-space/media \
    /var/www/student-space/public \
    /var/www/student-space/logs

# Copy Apache configuration
COPY docker/apache-config.conf /etc/apache2/sites-available/student-space.conf

# Enable site and required Apache modules
RUN a2dissite 000-default && \
    a2ensite student-space && \
    a2enmod rewrite headers ssl proxy proxy_http

# Copy Passenger WSGI file
COPY docker/passenger_wsgi.py /var/www/student-space/passenger_wsgi.py

# Copy entrypoint script
COPY docker/entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

# Set proper permissions
RUN chown -R app:app /var/www/student-space && \
    chmod -R 755 /var/www/student-space

# Expose HTTP port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# Use baseimage-docker's init system
CMD ["/sbin/my_init"]
