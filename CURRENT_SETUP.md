# Текущая настройка подключения к PostgreSQL

## База данных

**PostgreSQL на Timeweb:**
- Host: `9558e7dd68bdade50224f6f1.twc1.net`
- Port: `5432`
- Database: `db_21day`
- User: `gen_user`
- Password: `kQIXN6%3B%7DFrB3ZA` (URL encoded)
- SSL: требуется сертификат `~/.cloud-certs/root.crt`

## Backend

Backend уже настроен на эту базу в `backend/config/database.js`.

## Что нужно сделать

1. ✅ Backend настроен на вашу PostgreSQL
2. ⏳ Проверить подключение backend к базе
3. ⏳ Решить проблему RLS (отключить или настроить)
4. ⏳ Продолжить миграцию компонентов на API
5. ⏳ Настроить переменные окружения для фронтенда

## Следующие шаги

1. Проверить, что backend может подключиться к базе
2. Если есть ошибки RLS - отключить их (временное решение)
3. Продолжить миграцию компонентов на API вместо Supabase клиента

