#!/bin/bash
# ══════════════════════════════════════════════════════════════════════════════
# HOPE RECEPTION CENTRE — NAMECHEAP VPS DEPLOYMENT SCRIPT
# Server IP: 162.0.224.189 | Domain: hopereceptioncenter.org
# ══════════════════════════════════════════════════════════════════════════════

set -e

echo "=== 1. Updating System Packages ==="
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y python3-pip python3-venv nginx git curl

echo "=== 2. Setting Up Project Directory ==="
sudo mkdir -p /var/www/hrc
sudo chown -R $USER:$USER /var/www/hrc

if [ ! -d "/var/www/hrc/.git" ]; then
    git clone https://github.com/twiinarides/hrc.git /var/www/hrc
else
    cd /var/www/hrc
    git pull origin main
fi

cd /var/www/hrc

echo "=== 3. Setting Up Virtual Environment ==="
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "=== 4. Running Migrations & Collecting Static Files ==="
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

echo "=== 5. Setting Up Gunicorn Systemd Service ==="
sudo bash -c 'cat <<EOF > /etc/systemd/system/hrc.service
[Unit]
Description=Hope Reception Centre Django Application
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/hrc
ExecStart=/var/www/hrc/venv/bin/gunicorn --workers 3 --bind unix:/var/www/hrc/hrc.sock config.wsgi:application

[Install]
WantedBy=multi-user.target
EOF'

sudo systemctl daemon-reload
sudo systemctl enable hrc
sudo systemctl restart hrc

echo "=== 6. Configuring Nginx Web Server ==="
sudo bash -c 'cat <<EOF > /etc/nginx/sites-available/hrc
server {
    listen 80;
    server_name hopereceptioncenter.org www.hopereceptioncenter.org 162.0.224.189;

    client_max_body_size 50M;

    location /static/ {
        alias /var/www/hrc/staticfiles/;
    }

    location /media/ {
        alias /var/www/hrc/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/hrc/hrc.sock;
    }
}
EOF'

sudo ln -sf /etc/nginx/sites-available/hrc /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

echo "=== 7. Enabling SSL Certificate (Certbot) ==="
sudo apt-get install -y certbot python3-certbot-nginx || true
sudo certbot --nginx -d hopereceptioncenter.org -d www.hopereceptioncenter.org --non-interactive --agree-tos -m contact@hopereceptioncenter.org || true

echo "══════════════════════════════════════════════════════════════════════════════"
echo "✅ DEPLOYMENT COMPLETE! Site live at https://hopereceptioncenter.org"
echo "══════════════════════════════════════════════════════════════════════════════"
