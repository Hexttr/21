# План миграции с Supabase на PostgreSQL

## Что нужно сделать:

### 1. Backend API (Node.js/Express)
- Создать Express сервер
- Подключение к PostgreSQL
- JWT аутентификация
- API endpoints для замены Supabase функций

### 2. Изменить фронтенд
- Заменить Supabase клиент на fetch к API
- Обновить AuthContext
- Обновить все компоненты, использующие Supabase

### 3. Edge Functions → API Endpoints
- `/api/auth/*` - аутентификация
- `/api/users/*` - управление пользователями
- `/api/lessons/*` - уроки
- `/api/ai-chat` - AI чат
- `/api/ai-quiz` - AI квиз
- `/api/ai-image` - генерация изображений

## Структура проекта:

```
backend/
  ├── server.js          # Express сервер
  ├── config/
  │   └── database.js    # Подключение к PostgreSQL
  ├── routes/
  │   ├── auth.js        # Аутентификация
  │   ├── users.js       # Пользователи
  │   ├── lessons.js     # Уроки
  │   └── ai.js          # AI функции
  ├── middleware/
  │   └── auth.js        # JWT middleware
  └── package.json

frontend/ (day21/)
  └── src/
      └── api/           # API клиент вместо Supabase
```

