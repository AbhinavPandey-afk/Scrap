FROM python:3.11-slim 

ENV DEBIAN_FRONTEND=noninteractive

# Install all system dependencies + distutils
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

# Install Google Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt install -y ./google-chrome-stable_current_amd64.deb && \
    rm ./google-chrome-stable_current_amd64.deb

# Optional: print installed Chrome version to build logs
RUN google-chrome --version

# Tell Selenium where Chrome is
ENV GOOGLE_CHROME_BIN=/usr/bin/google-chrome

# App code location
WORKDIR /app

# Copy source files
COPY . .

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
CMD ["python", "app.py"]
