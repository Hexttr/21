# 21 Days Club - Deployment

Проект развертывания приложения на домене 21days.club

## Сервер
- IP: 195.133.63.34
- Пользователь: root
- Домен: 21days.club

## Развертывание

### Установка зависимостей
```bash
pip install -r requirements.txt
```

### Вариант 1: Автоматическое развертывание (уже выполнено)
```bash
python deploy.py
```

Скрипт автоматически:
1. Подключается к серверу через SSH
2. Обновляет систему
3. Устанавливает необходимые пакеты (Docker, Nginx, Certbot)
4. Настраивает Nginx
5. Настраивает firewall
6. Пытается установить SSL сертификат (требует настройки DNS)

### Вариант 2: Развертывание локального репозитория

Если у вас есть доступ к исходному репозиторию:

1. **Клонируйте репозиторий локально:**
   ```bash
   git clone https://github.com/luckyit-test/day21.git
   ```

2. **Или скачайте ZIP архив** с GitHub и распакуйте в папку `day21`

3. **Запустите скрипт развертывания:**
   ```bash
   python deploy_local_repo.py day21
   ```
   
   Или просто:
   ```bash
   python deploy_local_repo.py
   ```
   (скрипт попытается найти репозиторий автоматически)

### Вариант 3: Использование токена доступа

Если репозиторий приватный, используйте токен:
```bash
python copy_repo_with_token.py YOUR_GITHUB_TOKEN
```

## Структура проекта

- `deploy.py` - основной скрипт развертывания сервера
- `deploy_local_repo.py` - развертывание локальных файлов на сервер
- `upload_files.py` - загрузка отдельных файлов на сервер
- `copy_repo.py` - копирование репозитория с сервера
- `copy_repo_with_token.py` - копирование с использованием токена
- `download_and_deploy.py` - скачивание и развертывание через ZIP
- `test_connection.py` - тест подключения к серверу
- `requirements.txt` - зависимости Python
- `README.md` - документация

## Настройка DNS и SSL

После развертывания нужно:

1. **Настроить DNS записи:**
   - `21days.club` → `195.133.63.34`
   - `www.21days.club` → `195.133.63.34`

2. **Установить SSL сертификат:**
   ```bash
   ssh root@195.133.63.34
   certbot --nginx -d 21days.club -d www.21days.club --non-interactive --agree-tos --email admin@21days.club --redirect
   ```

## Полезные команды

```bash
# Проверить подключение к серверу
python test_connection.py

# Загрузить файлы на сервер
python upload_files.py

# Посмотреть логи Nginx
ssh root@195.133.63.34 "tail -f /var/log/nginx/error.log"
```

