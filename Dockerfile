FROM python:3.11-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Robocorp
RUN pip install --no-cache-dir robocorp robocorp-browser playwright requests openpyxl

WORKDIR /app

# Copy application files
COPY requirements.txt .
COPY tasks.py .
COPY robot.yaml .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers - this is the critical step
RUN playwright install chromium

# Create output directory
RUN mkdir -p output/work-items-in output/work-items-out output/shared_drive

# Run the consumer task
CMD ["python", "tasks.py", "consumer"]
