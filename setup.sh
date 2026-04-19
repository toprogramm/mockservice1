#!/bin/bash
# setup.sh — запускать от root на чистой Ubuntu 22.04 / 24.04
set -e

APP_DIR="/opt/mock_service"
SSL_DIR="/etc/nginx/ssl"
SERVER_IP=$(hostname -I | awk '{print $1}')   # первый IP машины

echo "=== 1. Устанавливаем зависимости ==="
apt-get update -qq
apt-get install -y python3 python3-venv python3-pip nginx openssl

echo "=== 2. Копируем приложение ==="
mkdir -p "$APP_DIR"
cp app.py "$APP_DIR/"

echo "=== 3. Создаём virtualenv и ставим Flask ==="
python3 -m venv "$APP_DIR/venv"
"$APP_DIR/venv/bin/pip" install --quiet flask

echo "=== 4. Генерируем самоподписанный сертификат (IP: $SERVER_IP) ==="
mkdir -p "$SSL_DIR"
openssl req -x509 -nodes -newkey rsa:2048 -days 3650 \
  -keyout "$SSL_DIR/mock.key" \
  -out    "$SSL_DIR/mock.crt" \
  -subj   "/CN=$SERVER_IP" \
  -addext "subjectAltName=IP:$SERVER_IP"

echo "=== 5. Подключаем конфиг nginx ==="
cp nginx_mock.conf /etc/nginx/conf.d/mock_service.conf
# Убираем дефолтный сайт если мешает
rm -f /etc/nginx/sites-enabled/default

nginx -t
systemctl reload nginx

echo "=== 6. Устанавливаем systemd-сервис ==="
cp mock_service.service /etc/systemd/system/mock_service.service
chown -R www-data:www-data "$APP_DIR"
systemctl daemon-reload
systemctl enable --now mock_service

echo ""
echo "======================================================"
echo " Готово!"
echo " Сервис доступен: https://$SERVER_IP/"
echo " Логин: aa    Пароль: aabb"
echo "======================================================"
