#!/bin/bash

# Update system packages
sudo apt update
sudo apt upgrade -y

# Install required system packages
sudo apt install -y python3-pip python3-venv ffmpeg nginx

# Create application directory
sudo mkdir -p /var/www/youtube-downloader
sudo chown -R $USER:$USER /var/www/youtube-downloader

# Copy application files
cp -r * /var/www/youtube-downloader/

# Create and activate virtual environment
cd /var/www/youtube-downloader
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
pip install gunicorn

# Create systemd service file
sudo tee /etc/systemd/system/youtube-downloader.service << EOF
[Unit]
Description=YouTube Downloader Flask Application
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=/var/www/youtube-downloader
Environment="PATH=/var/www/youtube-downloader/venv/bin"
ExecStart=/var/www/youtube-downloader/venv/bin/gunicorn --workers 3 --bind unix:youtube-downloader.sock -m 007 app:app

[Install]
WantedBy=multi-user.target
EOF

# Create Nginx configuration
sudo tee /etc/nginx/sites-available/youtube-downloader << EOF
server {
    listen 80;
    server_name 68.233.119.234;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/youtube-downloader/youtube-downloader.sock;
    }

    location /downloads {
        internal;
        alias /var/www/youtube-downloader/downloads;
    }

    # Increase timeouts for long downloads
    client_max_body_size 32M;
    proxy_connect_timeout 600;
    proxy_send_timeout 600;
    proxy_read_timeout 600;
    send_timeout 600;

    # Add security headers
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-XSS-Protection "1; mode=block";
    add_header X-Content-Type-Options "nosniff";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    # Enable gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
EOF

# Create downloads directory with proper permissions
mkdir -p /var/www/youtube-downloader/downloads
chmod 755 /var/www/youtube-downloader/downloads

# Enable and configure Nginx
sudo ln -s /etc/nginx/sites-available/youtube-downloader /etc/nginx/sites-enabled
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t

# Start and enable services
sudo systemctl start youtube-downloader
sudo systemctl enable youtube-downloader
sudo systemctl restart nginx

echo "Deployment complete! Check the application at http://your_domain_or_ip" 