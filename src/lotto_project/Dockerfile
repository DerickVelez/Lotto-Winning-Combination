# Use official Playwright base image (includes Python + browser deps)
FROM mcr.microsoft.com/playwright/python:v1.52.0-noble

# Copy uv binary for dependency installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install system dependencies
RUN apt-get update && apt-get install -yq --no-install-recommends \
    curl \
    git \
    build-essential \
    libnss3 \
    libatk-bridge2.0-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libasound2t64 \
    libgtk-3-0 \
    libdrm2 \
    libgbm1 \
    libpango-1.0-0 \
    libxshmfence1 \
    libxss1 \
    libxtst6 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency and workspace config
COPY pyproject.toml ./
COPY workspace.yaml ./

# Copy app source code
COPY ./src ./src

# Install Python dependencies
RUN uv sync




# Expose Dagster webserver port
EXPOSE 3000

# Start Dagster webserver
CMD ["uv", "run", "dagster", "dev", "-h", "0.0.0.0", "-p", "3000"]
