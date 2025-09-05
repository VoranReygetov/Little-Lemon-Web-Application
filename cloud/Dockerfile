# Use a slim Python base image
ARG PYTHON_VERSION=3.11.9
FROM python:${PYTHON_VERSION}-slim AS builder

# Install system dependencies required by mysqlclient
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
 && apt-get upgrade -y \
 && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

RUN chmod +x  /app/entrycloud.prod.sh

# Use Gunicorn as entrypoint for Django
CMD ["/app/entrycloud.prod.sh"]


