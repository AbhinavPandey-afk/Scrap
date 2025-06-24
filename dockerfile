# Use Python 3.11 slim image
FROM python:3.11-slim

# Avoid interaction during package install
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies for Chrome and fonts
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    unzip \
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
    xdg-utils \
    libasound2 \
    ca-certificates \
    google-chrome-stable \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Download and install Chrome manually
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb

# Set environment variable for Chrome binary path
ENV GOOGLE_CHROME_BIN=/usr/bin/google-chrome

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port for Flask
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]
