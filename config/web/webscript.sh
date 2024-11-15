#!/bin/sh

# ------------------------------
# webscript.sh - Entrypoint Script for Customer Order Service Django Application
# ------------------------------

set -e  # Exit immediately on error
set -u  # Treat unset variables as errors

LOG_FILE="/cust_backend/logs/django_setup.log"
mkdir -p /cust_backend/logs /cust_backend/staticfiles
touch "$LOG_FILE"
chmod 775 "$LOG_FILE"

echo "Starting Django application setup..." | tee -a "$LOG_FILE"

# Environment variables (sensitive data masked)
echo "Environment Variables:" | tee -a "$LOG_FILE"
echo "POSTGRES_DB: ${POSTGRES_DB}" | tee -a "$LOG_FILE"
echo "POSTGRES_USER: ${POSTGRES_USER}" | tee -a "$LOG_FILE"
echo "POSTGRES_PASSWORD: [REDACTED]" | tee -a "$LOG_FILE"
echo "POSTGRES_HOST: ${POSTGRES_HOST}" | tee -a "$LOG_FILE"
echo "POSTGRES_PORT: ${POSTGRES_PORT}" | tee -a "$LOG_FILE"

# ------------------------------
# Function: Wait for PostgreSQL readiness
# ------------------------------
wait_for_postgres() {
    echo "Waiting for PostgreSQL database to be ready..." | tee -a "$LOG_FILE"
    until dockerize -wait tcp://"$POSTGRES_HOST":"$POSTGRES_PORT" -timeout 120s; do
        echo "PostgreSQL not ready, retrying in 5 seconds..." | tee -a "$LOG_FILE"
        sleep 5
    done
}

# ------------------------------
# Enhanced Command Execution with Retry
# ------------------------------
run_command() {
    cmd="$1"
    retries=2
    count=0

    while [ "$count" -lt "$retries" ]; do
        sh -c "$cmd" >> "$LOG_FILE" 2>&1 && break
        count=$((count + 1))
        if [ "$count" -lt "$retries" ]; then
            echo "Command failed: $cmd. Retrying ($count/$retries)..." | tee -a "$LOG_FILE"
            sleep 5
        else
            echo "Command failed after $retries attempts: $cmd" | tee -a "$LOG_FILE"
            sh -c "$cmd" 2>&1 | tee -a "$LOG_FILE"
            exit 1
        fi
    done
}

# ------------------------------
# Run Unit Tests
# ------------------------------
run_tests() {
    echo "Running unit tests..." | tee -a "$LOG_FILE"
    run_command "pytest /cust_backend/app/customerorder/tests/unit/test_cust.py"
    echo "Unit tests passed successfully." | tee -a "$LOG_FILE"
}

# ------------------------------
# Django Setup - Migrations and Static Collection
# ------------------------------
setup_django() {
    echo "Making migrations for project apps..." | tee -a "$LOG_FILE"
    run_command "python ./manage.py makemigrations customerorder"

    echo "Applying database migrations..." | tee -a "$LOG_FILE"
    run_command "python ./manage.py migrate"

    echo "Collecting static files..." | tee -a "$LOG_FILE"
    run_command "python ./manage.py collectstatic --noinput"
}

# ------------------------------
# Start Gunicorn Server
# ------------------------------
start_server() {
    echo "Starting Gunicorn with Uvicorn workers..." | tee -a "$LOG_FILE"
    exec gunicorn app.main.asgi:application \
        --bind 0.0.0.0:8000 \
        --workers 4 \
        --worker-class uvicorn.workers.UvicornWorker \
        --log-level debug \
        >> "$LOG_FILE" 2>&1 || { echo "Gunicorn failed to start" | tee -a "$LOG_FILE"; exit 1; }

    # Health check for Gunicorn server
    sleep 5  # Wait briefly to allow the server to start
    curl -s http://localhost:8000/health || { echo "Health check failed" | tee -a "$LOG_FILE"; exit 1; }
}

# ------------------------------
# Main Execution Sequence
# ------------------------------

trap 'echo "Received termination signal, shutting down..." | tee -a "$LOG_FILE"; exit 0' TERM INT

run_tests
wait_for_postgres
setup_django
start_server

echo "Django application setup completed successfully!" | tee -a "$LOG_FILE"
