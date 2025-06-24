# Use Python 3.11 slim image
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies and distutils
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg \
    python3-distutils \
    fonts-liberation \
    libnss3 \
    libxss1 \
    libappindicator1 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libasound2 \
    xdg-utils \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Install Google Chrome manually
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb

# Optional: Confirm Chrome install in logs
RUN google-chrome --version

# Set environment variable for Chrome path (used by Selenium)
ENV GOOGLE_CHROME_BIN=/usr/bin/google-chrome

# Set app directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the default Flask port
EXPOSE 5000

# Start Flask app
CMD ["python", "app.py"]
