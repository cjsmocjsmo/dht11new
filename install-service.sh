#!/bin/bash

# DHT11 Monitor Service Installation Script
# This script installs the systemd service for the DHT11 temperature monitor

SERVICE_NAME="dht11-monitor"
SERVICE_FILE="$SERVICE_NAME.service"
SYSTEMD_PATH="/etc/systemd/system"

echo "Installing DHT11 Monitor Service..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run this script as root (use sudo)"
    exit 1
fi

# Check if service file exists
if [ ! -f "$SERVICE_FILE" ]; then
    echo "Error: $SERVICE_FILE not found in current directory"
    exit 1
fi

# Copy service file to systemd directory
echo "Copying service file to $SYSTEMD_PATH..."
cp "$SERVICE_FILE" "$SYSTEMD_PATH/"

# Set proper permissions
chmod 644 "$SYSTEMD_PATH/$SERVICE_FILE"

# Reload systemd daemon
echo "Reloading systemd daemon..."
systemctl daemon-reload

# Enable the service to start on boot
echo "Enabling service to start on boot..."
systemctl enable "$SERVICE_NAME"

# Start the service now
echo "Starting the service..."
systemctl start "$SERVICE_NAME"

# Check service status
echo "Service status:"
systemctl status "$SERVICE_NAME" --no-pager

echo ""
echo "Installation complete!"
echo ""
echo "Useful commands:"
echo "  View service status:    sudo systemctl status $SERVICE_NAME"
echo "  Start service:          sudo systemctl start $SERVICE_NAME"
echo "  Stop service:           sudo systemctl stop $SERVICE_NAME"
echo "  Restart service:        sudo systemctl restart $SERVICE_NAME"
echo "  View logs:              sudo journalctl -u $SERVICE_NAME -f"
echo "  Disable auto-start:     sudo systemctl disable $SERVICE_NAME"
echo ""