# Passenger + Apache Docker Environment
# Simulates Domainesia cPanel + Passenger setup for local testing

FROM phusion/passenger-customizable:3.0.5

# Set maintainer
LABEL maintainer="student-space"
LABEL description="Local Passenger testing environment for Student Space"

# Import Passenger repo signing key required by newer apt versions
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys D870AB033FB45BD1

# Enable Passenger + Apache
RUN /pd_build/python.sh

# Install runtime packages
RUN apt-get update && \
    apt-get install -y \
        python3 \
        python3-dev \
        python3-venv \
        python3-pip \
        apache2 \
        libapache2-mod-passenger \
        libpq-dev \
        postgresql-client \
        netcat-openbsd \
        vim \
        curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Create virtualenv in similar location as cPanel
RUN python3 -m venv /var/www/venv
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
COPY deploy/apache/student-space.conf /etc/apache2/sites-available/student-space.conf

# Enable site and required Apache modules
RUN a2dissite 000-default && \
    a2ensite student-space && \
    a2enmod passenger rewrite headers ssl proxy proxy_http

# Copy entrypoint script
COPY deploy/scripts/docker-entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Set proper permissions
RUN chown -R app:app /var/www/student-space && \
    chmod -R 755 /var/www/student-space

# Expose HTTP port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# Run project entrypoint (it boots /sbin/my_init internally)
CMD ["/usr/local/bin/entrypoint.sh"]
