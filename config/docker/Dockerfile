# Use the official Python Debian-based image
FROM python:3.12-slim

# Set environment variables to disable .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies and Dockerize
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        wget \
        bash \
        curl \
        libffi-dev \
        libssl-dev \
        dos2unix && \
    wget https://github.com/jwilder/dockerize/releases/download/v0.6.1/dockerize-linux-amd64-v0.6.1.tar.gz && \
    tar -C /usr/local/bin -xzvf dockerize-linux-amd64-v0.6.1.tar.gz && \
    rm dockerize-linux-amd64-v0.6.1.tar.gz && \
    apt-get remove -y build-essential && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Set the working directory in the container and define PYTHONPATH
WORKDIR /cust_backend
ENV PYTHONPATH=/cust_backend:/cust_backend/app


# Copy requirements and install Python dependencies
COPY ../../requirements.txt .
RUN pip install -r requirements.txt --verbose

# Copy the entire project directory into the container
COPY . /cust_backend/

# Make the script executable and convert line endings to Unix format
RUN chmod +x ./config/web/webscript.sh && \
    dos2unix ./config/web/webscript.sh
# Add a non-root user and group, and assign ownership to all files
RUN addgroup --system rootgroup && \
    adduser --system --ingroup rootgroup rootdockeruser && \
    chown -R rootdockeruser:rootgroup /cust_backend

# Create necessary directories for static files, logs, and Firebase configuration
# Set the staticfiles and logs directories to be writable by rootdockeruser
RUN mkdir -p /cust_backend/staticfiles /cust_backend/logs /cust_backend/config/firebase && \
    chown -R rootdockeruser:rootgroup /cust_backend/staticfiles /cust_backend/logs /cust_backend/config && \
    chmod -R 775 /cust_backend/staticfiles /cust_backend/logs /cust_backend/config


# Switch to the non-root user
USER rootdockeruser

# Expose the application port
EXPOSE 8000

# Command to run the startup script within Docker
CMD ["bash", "./config/web/webscript.sh"]
