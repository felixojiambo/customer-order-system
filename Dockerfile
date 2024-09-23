# Use the official Python image
FROM python:3.12

# Set the working directory in the container
WORKDIR /code

# Copy the current directory contents into the container
COPY . /code/

# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt
# Install coverage and pytest for running tests
RUN pip install --no-cache-dir coverage pytest

# Define environment variable for Django settings module
ENV DJANGO_SETTINGS_MODULE=customer_order_service.settings

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Command to run tests with coverage (optional: you can comment this out if not running tests)
# RUN coverage run -m pytest custorder/tests
# CMD ["coverage", "report"]  # to show coverage after tests

# Default command to run the Django app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
