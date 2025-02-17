# Use Raspberry Pi OS Bullseye base image
FROM arm32v7/debian:bullseye-slim

# Add Raspberry Pi OS repository and keys
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

RUN wget -qO - https://archive.raspberrypi.org/debian/raspberrypi.gpg.key | apt-key add - \
    && echo "deb http://archive.raspberrypi.org/debian/ bullseye main" > /etc/apt/sources.list.d/raspi.list

# Install required system packages
# - libzbar0 and zbar-tools for pyzbar (barcode scanning)
# - python3-smbus for I2C (used by smbus)
# - python3-spidev if you need SPI
RUN apt-get update && apt-get install -y \
    thonny \
    x11-apps \
    python3 \
    python3-pip \
    libcamera0 \
    libcamera-apps \
    python3-picamera2 \
    python3-rpi.gpio \
    v4l-utils \
    i2c-tools \
    python3-opencv \
    libatlas-base-dev \
    zbar-tools \
    libzbar0 \
    build-essential \
    python3-dev \
    python3-smbus \
    python3-spidev \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy all project files into the app directory
COPY . .

# Install Python dependencies from requirements.txt
# Make sure 'pyzbar' is listed in your requirements.txt
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -i https://pypi.org/simple opencv-python-headless &&\
    pip3 install --no-cache-dir -r requirements.txt


RUN pip3 install --upgrade pip && pip3 install --no-cache-dir spidev
RUN pip3 install --no-cache-dir smbus2
# Set the script to run as root to access the camera and hardware
USER root

CMD ["bash", "-c", "python3 app.py"]

