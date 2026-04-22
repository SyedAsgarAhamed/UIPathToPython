FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install basic system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set Playwright browser path to a local directory within the app
ENV PLAYWRIGHT_BROWSERS_PATH=/app/pw-browsers

# Install Playwright browsers + all system dependencies
RUN playwright install --with-deps chromium


# Copy app
COPY . .

# Create output directories
RUN mkdir -p output/work-items-in output/shared_drive

CMD ["python", "tasks.py", "run_all"]