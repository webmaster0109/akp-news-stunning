#
# --- Build Stage ---
#
# This stage is used to install dependencies and build the application.
# It includes build tools that are not needed in the final runtime image.
#
FROM python:3.12-slim-bookworm AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies needed for building Python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Create a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


#
# --- Runtime Stage ---
#
# This is the final stage that will be used to run the application.
# It's a minimal image that only contains the necessary code and dependencies.
#
FROM python:3.12-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install runtime system dependencies
# libpq5 is required for psycopg2 to connect to PostgreSQL
# libstdc++6 is required for pymupdf
# lsof and procps are useful for debugging running containers
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 \
    libstdc++6 \
    lsof \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security
RUN addgroup --system app && adduser --system --group app

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy the application code
WORKDIR /app
COPY . .

# Set ownership of the app directory to the non-root user
RUN chown -R app:app /app

# Switch to the non-root user
USER app

# Set the path to include the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Expose the port Gunicorn will run on
EXPOSE 8000

# The command to run the application
CMD ["gunicorn", "--config", "gunicorn.conf.py", "akp_server.wsgi:application"]