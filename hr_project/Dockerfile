# Dockerfile for HR Portal on Render

FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Make entrypoint executable
RUN chmod +x /app/docker-entrypoint.sh

# Expose port (Koyeb sets $PORT; default to 8000 for local)
ENV PORT=8000
EXPOSE 8000

# Entrypoint runs migrations + collectstatic, then the passed command
# (gunicorn for web, or `celery -A hr_project worker` for the worker service)
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["gunicorn", "hr_project.wsgi:application", "--bind", "0.0.0.0:8000", "--log-file", "-"]