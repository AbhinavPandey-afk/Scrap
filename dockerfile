# Use a lightweight Python image
FROM python:3.11-slim

# Avoid interaction during build
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies and Google Chrome manually
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg \
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
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Add the Chrome APT repo
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Set environment variable to point to Chrome
ENV GOOGLE_CHROME_BIN=/usr/bin/google-chrome

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Flask port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
