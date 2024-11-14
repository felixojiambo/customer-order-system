#!/bin/sh

# webscript.sh - Entrypoint Script for the Customer Order Service Django Application

# Exit immediately if a command exits with a non-zero status
set -e
# Use `set -u` to treat unset variables as an error
set -u

# Log file location
LOG_FILE="/cust_backend/logs/django_setup.log"
mkdir -p /cust_backend/logs
touch "$LOG_FILE"
chmod 775 "$LOG_FILE"

# Logging start of the script
echo "Starting the Django application setup..." | tee -a "$LOG_FILE"

# Print environment variables (mask sensitive data)
echo "Environment Variables:" | tee -a "$LOG_FILE"
echo "POSTGRES_DB: ${POSTGRES_DB}" | tee -a "$LOG_FILE"
echo "POSTGRES_USER: ${POSTGRES_USER}" | tee -a "$LOG_FILE"
echo "POSTGRES_PASSWORD: [REDACTED]" | tee -a "$LOG_FILE"
echo "POSTGRES_HOST: ${POSTGRES_HOST}" | tee -a "$LOG_FILE"
echo "POSTGRES_PORT: ${POSTGRES_PORT}" | tee -a "$LOG_FILE"

# Function to wait for PostgreSQL to be ready
wait_for_postgres() {
    echo "Waiting for PostgreSQL database to be ready..." | tee -a "$LOG_FILE"
    until dockerize -wait tcp://"$POSTGRES_HOST":"$POSTGRES_PORT" -timeout 120s
    do
        echo "PostgreSQL not ready, retrying in 5 seconds..." | tee -a "$LOG_FILE"
        sleep 5
    done
}

# Enhanced run_command function for better error handling and logging
run_command() {
    cmd="$1"
    retries=2
    count=0

    while [ "$count" -lt "$retries" ]; do
        # Execute the command and append output to the log file
        sh -c "$cmd" >> "$LOG_FILE" 2>&1 && break
        count=$((count + 1))
        if [ "$count" -lt "$retries" ]; then
            echo "Command failed: $cmd. Retrying ($count/$retries)..." | tee -a "$LOG_FILE"
            sleep 5
        else
            echo "Command failed after $retries attempts: $cmd" | tee -a "$LOG_FILE"
            echo "Full error output for $cmd:" | tee -a "$LOG_FILE"
            # Output the last error to the console for immediate feedback
            sh -c "$cmd" 2>&1 | tee -a "$LOG_FILE"
            exit 1
        fi
    done
}

# Trap signals to ensure graceful shutdown
trap 'echo "Received termination signal, shutting down..." | tee -a "$LOG_FILE"; exit 0' TERM INT

# Function to run unit tests
run_tests() {
    echo "Running unit tests..." | tee -a "$LOG_FILE"
    run_command "pytest /cust_backend/app/customerorder/tests/unit/test_cust.py"

    echo "Unit tests passed successfully." | tee -a "$LOG_FILE"
}

# Function to run migrations and collect static files
setup_django() {
    echo "Making migrations..." | tee -a "$LOG_FILE"
    run_command "python ./manage.py makemigrations"

    echo "Applying database migrations..." | tee -a "$LOG_FILE"
    run_command "python ./manage.py migrate"

    # Collect static files
    echo "Collecting static files..." | tee -a "$LOG_FILE"
    run_command "python ./manage.py collectstatic --noinput"
}

# Function to start the Gunicorn server
start_server() {
    echo "Starting Gunicorn with Uvicorn workers..." | tee -a "$LOG_FILE"
    exec gunicorn app.main.asgi:application \
        --bind 0.0.0.0:8000 \
        --workers 4 \
        --worker-class uvicorn.workers.UvicornWorker \
        >> "$LOG_FILE" 2>&1
}

# Run unit tests
run_tests

# Wait for PostgreSQL to be ready
wait_for_postgres

# Set up Django (migrations and static files)
setup_django

# Start the server
start_server

# Logging Setup Completion
echo "Django application setup completed unsuccessfully!" | tee -a "$LOG_FILE"
