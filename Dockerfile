# Use official Python 3.12 Alpine image
FROM python:3.12-alpine

# Install system dependencies for SSL and build tools
RUN apk add --no-cache gcc musl-dev libffi-dev openssl openssl-dev ca-certificates

# Set work directory
WORKDIR /app

# Copy project files
COPY . /app

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip \
    && pip install uv


# Export dependencies to requirements.txt using uv
RUN uv pip compile pyproject.toml --all-extras --output-file requirements.txt

# Install dependencies via pip
RUN pip install --no-cache-dir -r requirements.txt

# Ensure SSL certificates are up to date
RUN update-ca-certificates

# Expose FastAPI port
EXPOSE 8000

# Command to run FastAPI app with Hypercorn
CMD ["python3", "main.py"]
