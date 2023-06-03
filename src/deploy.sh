#!/bin/bash

# Create the systemd service unit file
sudo tee /etc/systemd/system/blahaj-api.service > /dev/null << EOF
[Unit]
Description=Blahaj API Service
After=network.target

[Service]
ExecStart=/usr/local/bin/gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
WorkingDirectory=/root/Blahaj
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl enable blahaj-api.service
sudo systemctl start blahaj-api.service

# Display the service status
sudo systemctl status blahaj-api.service
