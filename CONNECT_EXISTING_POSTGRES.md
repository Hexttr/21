# Подключение существующей PostgreSQL базы данных

## Текущая ситуация

У нас есть:
- ✅ **PostgreSQL база данных на Timeweb:**
  - Host: `9558e7dd68bdade50224f6f1.twc1.net`
  - Port: `5432`
  - Database: `db_21day`
  - User: `gen_user`
  - Password: `kQIXN6%3B%7DFrB3ZA` (URL encoded)
  - SSL: требуется сертификат

- ✅ **Данные уже мигрированы** в эту базу
- ✅ **Backend API создан** и готов к подключению

## Что нужно сделать

1. ✅ Backend уже настроен на эту базу (в `backend/config/database.js`)
2. ⏳ Убедиться, что SSL сертификат установлен на сервере
3. ⏳ Решить проблему RLS (Row Level Security)
4. ⏳ Продолжить миграцию компонентов на API
5. ⏳ Настроить переменные окружения для фронтенда

## Текущая конфигурация backend

Backend уже настроен на использование вашей PostgreSQL базы:
- Connection string: `postgresql://gen_user:kQIXN6%3B%7DFrB3ZA@9558e7dd68bdade50224f6f1.twc1.net:5432/db_21day?sslmode=verify-full`
- SSL сертификат: `~/.cloud-certs/root.crt`

## Следующие шаги

1. Проверить подключение backend к базе
2. Решить проблему RLS (отключить или настроить политики)
3. Продолжить миграцию компонентов на API
4. Настроить фронтенд для работы с API

