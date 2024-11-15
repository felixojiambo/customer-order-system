#!/bin/bash

# ------------------------------
# webscript.sh - Entrypoint Script for Customer Order Service Django Application
# ------------------------------

set -e  # Exit on error
set -o pipefail
set -o nounset
set -o xtrace

LOG_FILE="/cust_backend/logs/django_setup.log"
mkdir -p /cust_backend/logs /cust_backend/staticfiles
touch "$LOG_FILE"
chmod 775 "$LOG_FILE"

# Log start of setup
echo "Starting the Django application setup..." | tee -a "$LOG_FILE"

# Print environment variables (mask sensitive data)
echo "Environment Variables:" | tee -a "$LOG_FILE"
echo "POSTGRES_DB: $POSTGRES_DB" | tee -a "$LOG_FILE"
echo "POSTGRES_USER: $POSTGRES_USER" | tee -a "$LOG_FILE"
echo "POSTGRES_PASSWORD: [REDACTED]" | tee -a "$LOG_FILE"
echo "POSTGRES_HOST: $POSTGRES_HOST" | tee -a "$LOG_FILE"
echo "POSTGRES_PORT: $POSTGRES_PORT" | tee -a "$LOG_FILE"

# Function: Wait for PostgreSQL to be ready
wait_for_postgres() {
    echo "Waiting for PostgreSQL to be ready..." | tee -a "$LOG_FILE"
    until dockerize -wait tcp://$POSTGRES_HOST:$POSTGRES_PORT -timeout 120s; do
        echo "PostgreSQL not ready, retrying in 5 seconds..." | tee -a "$LOG_FILE"
        sleep 5
    done
}

# Function: Run command with retries
run_command() {
    local cmd="$1"
    local retries=2
    local count=0

    until bash -c "$cmd" >> "$LOG_FILE" 2>&1; do
        count=$((count + 1))
        if [ $count -lt $retries ]; then
            echo "Command failed: $cmd. Retrying ($count/$retries)..." | tee -a "$LOG_FILE"
            sleep 5
        else
            echo "Command failed after $retries attempts: $cmd" | tee -a "$LOG_FILE"
            bash -c "$cmd" 2>&1 | tee -a "$LOG_FILE"
            exit 1
        fi
    done
}

# Wait for PostgreSQL
wait_for_postgres

# Django setup tasks
echo "Running migrations..." | tee -a "$LOG_FILE"
run_command "python ./manage.py makemigrations customerorder"
run_command "python ./manage.py migrate"

echo "Collecting static files..." | tee -a "$LOG_FILE"
run_command "python ./manage.py collectstatic --noinput"

# Start Gunicorn server with Uvicorn workers
echo "Starting Gunicorn with Uvicorn workers..." | tee -a "$LOG_FILE"
# shellcheck disable=SC2093
exec gunicorn app.main.asgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    >> "$LOG_FILE" 2>&1

echo "Django application setup completed successfully!" | tee -a "$LOG_FILE"
