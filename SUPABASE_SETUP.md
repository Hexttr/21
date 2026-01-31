# Настройка Supabase для миграции на PostgreSQL

## Получение Connection String

### Способ 1: Через Supabase Dashboard
1. Войдите в [Supabase Dashboard](https://supabase.com/dashboard)
2. Выберите проект `uyymukgccsqzagpusswm`
3. Перейдите в **Settings** → **Database**
4. Найдите **Connection string** → **URI**
5. Скопируйте connection string

### Способ 2: Формат connection string
```
postgresql://postgres.[project-ref]:[password]@db.[project-ref].supabase.co:5432/postgres
```

Где:
- `[project-ref]` = `uyymukgccsqzagpusswm`
- `[password]` = пароль базы данных (нужно получить из Dashboard)

### Способ 3: Pooler connection (рекомендуется)
```
postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres?pgbouncer=true
```

## Настройка переменных окружения

### Frontend (.env)
```env
VITE_SUPABASE_URL=https://uyymukgccsqzagpusswm.supabase.co
VITE_SUPABASE_PUBLISHABLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV5eW11a2djY3NxemFncHVzc3dtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgxNTIzMDksImV4cCI6MjA4MzcyODMwOX0.IkUJbJPXO5zNuB-9oEZs0v38zHYrkoSc1ofniHSJM9M
VITE_SUPABASE_PROJECT_ID=uyymukgccsqzagpusswm
```

### Backend (.env)
```env
# PostgreSQL connection (получить из Supabase Dashboard)
DATABASE_URL=postgresql://postgres.[project-ref]:[password]@db.[project-ref].supabase.co:5432/postgres

# Или использовать pooler
DATABASE_URL=postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres?pgbouncer=true

# JWT secret для backend
JWT_SECRET=your-secret-key-here

# OpenAI API key (опционально)
OPENAI_API_KEY=your-openai-key-here
```

## Важные моменты

1. **Пароль базы данных:** Нужно получить из Supabase Dashboard (Settings → Database → Database password)
2. **SSL:** Supabase требует SSL подключение
3. **RLS:** Row Level Security может быть включен, нужно будет отключить или настроить политики
4. **Edge Functions:** Если используем, они остаются в Supabase

## Следующие шаги

1. Получить connection string из Supabase Dashboard
2. Обновить `backend/.env` с connection string
3. Обновить backend для использования нового connection string
4. Продолжить миграцию компонентов на API

