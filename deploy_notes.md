# Заметки по развертыванию

## Статус развертывания

✅ Сервер настроен
✅ Nginx настроен для домена 21days.club
✅ Firewall настроен (порты 22, 80, 443)
⏳ SSL сертификат - ожидает настройки DNS
⏳ Исходный репозиторий - требуется доступ

## Что нужно сделать

### 1. Настроить DNS
Добавить A-записи для домена 21days.club:
- `21days.club` → `195.133.63.34`
- `www.21days.club` → `195.133.63.34`

### 2. Установить SSL сертификат
После настройки DNS выполнить на сервере:
```bash
certbot --nginx -d 21days.club -d www.21days.club --non-interactive --agree-tos --email admin@21days.club --redirect
```

### 3. Получить исходный код
Если репозиторий https://github.com/luckyit-test/day21.git приватный, нужно:
- Добавить SSH ключ на сервер
- Или использовать токен доступа для клонирования

## Структура на сервере

- Приложение: `/var/www/21days.club`
- Nginx конфиг: `/etc/nginx/sites-available/21days.club`
- Логи: `/var/log/nginx/`

## Команды для управления

```bash
# Перезагрузить Nginx
systemctl reload nginx

# Проверить статус Nginx
systemctl status nginx

# Проверить SSL сертификат
certbot certificates

# Обновить SSL сертификат вручную
certbot renew
```

