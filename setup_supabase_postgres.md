# Настройка подключения к PostgreSQL через Supabase

## Шаг 1: Получить Connection String

### Через Supabase Dashboard:
1. Откройте https://supabase.com/dashboard
2. Войдите в проект `uyymukgccsqzagpusswm`
3. Перейдите: **Settings** → **Database**
4. Найдите раздел **Connection string**
5. Выберите **URI** (не Session mode)
6. Скопируйте connection string

Формат будет примерно таким:
```
postgresql://postgres.uyymukgccsqzagpusswm:[PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

Или прямой connection:
```
postgresql://postgres.uyymukgccsqzagpusswm:[PASSWORD]@db.uyymukgccsqzagpusswm.supabase.co:5432/postgres
```

**Важно:** Замените `[PASSWORD]` на реальный пароль базы данных (если не знаете, можно сбросить в Dashboard).

## Шаг 2: Обновить Backend

После получения connection string, обновим `backend/config/database.js`:

```javascript
// Использовать connection string из Supabase
const connectionString = process.env.DATABASE_URL || 'postgresql://...';
```

## Шаг 3: Настроить переменные окружения

Создать/обновить `backend/.env`:
```env
DATABASE_URL=postgresql://postgres.uyymukgccsqzagpusswm:[PASSWORD]@db.uyymukgccsqzagpusswm.supabase.co:5432/postgres
JWT_SECRET=your-secret-key
OPENAI_API_KEY=your-key-if-needed
PORT=3001
```

## Шаг 4: SSL сертификат

Supabase использует SSL. Нужно либо:
- Использовать `sslmode=require` в connection string
- Или скачать SSL сертификат Supabase

## Что дальше?

После получения connection string:
1. Обновлю `backend/config/database.js`
2. Обновлю `backend/.env` на сервере
3. Перезапущу backend
4. Продолжу миграцию компонентов

