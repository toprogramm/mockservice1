# Mock Service — инструкция по запуску

## Структура файлов

```
app.py                  — Flask-приложение (всё в одном файле)
nginx_mock.conf         — конфиг nginx (HTTPS reverse proxy)
mock_service.service    — systemd unit
setup.sh                — скрипт автоматической установки
```

---

## Быстрый старт (одна команда)

```bash
sudo bash setup.sh
```

Скрипт сам:
- установит `python3`, `nginx`, `openssl`
- создаст virtualenv с Flask
- сгенерирует самоподписанный TLS-сертификат на IP машины
- настроит nginx как HTTPS-прокси на порту 443
- зарегистрирует и запустит systemd-сервис

После окончания в консоли появится URL вида `https://192.168.x.x/`.

---

## Ручная установка (шаг за шагом)

```bash
# 1. Зависимости
sudo apt update && sudo apt install -y python3 python3-venv nginx openssl

# 2. Приложение
sudo mkdir -p /opt/mock_service
sudo cp app.py /opt/mock_service/
sudo python3 -m venv /opt/mock_service/venv
sudo /opt/mock_service/venv/bin/pip install flask

# 3. Сертификат (замените IP на свой)
SERVER_IP="192.168.1.100"
sudo mkdir -p /etc/nginx/ssl
sudo openssl req -x509 -nodes -newkey rsa:2048 -days 3650 \
  -keyout /etc/nginx/ssl/mock.key \
  -out    /etc/nginx/ssl/mock.crt \
  -subj   "/CN=$SERVER_IP" \
  -addext "subjectAltName=IP:$SERVER_IP"

# 4. nginx
sudo cp nginx_mock.conf /etc/nginx/conf.d/mock_service.conf
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

# 5. systemd
sudo cp mock_service.service /etc/systemd/system/
sudo chown -R www-data:www-data /opt/mock_service
sudo systemctl daemon-reload
sudo systemctl enable --now mock_service
```

---

## Проверка работы

```bash
# Статус сервиса
systemctl status mock_service

# Логи
journalctl -u mock_service -f

# Тест через curl (игнорируем самоподписанный cert)
IP="192.168.1.100"

# 1. Получаем страницу логина (видим __secretToken)
curl -k -c cookies.txt https://$IP/signin

# 2. Логинимся
curl -k -c cookies.txt -b cookies.txt -X POST https://$IP/signin \
  -d "__secretToken=superSecretToken&login=aa&password=aabb"

# 3. Смотрим /index и /version
curl -k -b cookies.txt https://$IP/index
curl -k -b cookies.txt https://$IP/version
```

---

## Маршруты

| Метод | Путь          | Описание                        |
|-------|---------------|---------------------------------|
| GET   | `/signin`     | Форма входа с `__secretToken`   |
| POST  | `/signin`     | Авторизация (form-urlencoded)   |
| GET   | `/index`      | Статус сервисов (Diagnostic)    |
| GET   | `/version`    | Версии сервисов                 |
| GET   | `/api/version`| Версия plain-text               |

**Логин:** `aa`  
**Пароль:** `aabb`  
**Токен:** `superSecretToken`

---

## Управление сервисом

```bash
systemctl stop    mock_service
systemctl start   mock_service
systemctl restart mock_service
```

---

## Изменить данные

Всё хардкодом в `app.py`:

- `INDEX_ITEMS` — список сервисов и их классы (`success` / `warning` / `danger`)
- `VERSION_ITEMS` — список сервисов с версиями, серверами, датами и классами
- `LOGIN`, `PASSWORD`, `SECRET_TOKEN` — учётные данные

После правки перезапустите сервис: `sudo systemctl restart mock_service`
