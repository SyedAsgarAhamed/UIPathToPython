FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install system dependencies for Playwright/Chromium (MISSING in your version)
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    libgtk-3-0 \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set Playwright browser path to match Robocorp's expected location
ENV PLAYWRIGHT_BROWSERS_PATH=/root/.robocorp/playwright

# Install Playwright browsers + deps
RUN playwright install-deps chromium
RUN playwright install chromium


# Copy app
COPY . .

# Create output directories
RUN mkdir -p output/work-items-in output/shared_drive

CMD ["python", "tasks.py", "run_all"]