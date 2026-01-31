# Миграция с Supabase на прямой PostgreSQL

## Текущая ситуация

У нас есть:
- **Supabase проект:** `uyymukgccsqzagpusswm`
- **Supabase URL:** `https://uyymukgccsqzagpusswm.supabase.co`
- **Supabase Anon Key:** (для аутентификации, если нужно)

## План миграции

### Вариант 1: Полный переход на PostgreSQL (РЕКОМЕНДУЕТСЯ)
1. Подключиться к PostgreSQL базе данных Supabase напрямую
2. Использовать наш backend API для всех операций
3. Убрать зависимость от Supabase клиента во фронтенде

### Вариант 2: Гибридный подход
1. Использовать Supabase Auth для аутентификации
2. Использовать прямой PostgreSQL для данных
3. Использовать наш backend API

## Что нужно сделать

1. ✅ Получить connection string к PostgreSQL базе Supabase
2. ✅ Настроить backend для подключения к этой базе
3. ✅ Продолжить миграцию фронтенда на API
4. ✅ Настроить переменные окружения

## Следующие шаги

1. Получить connection string к PostgreSQL базе данных Supabase
2. Обновить backend для использования этого connection string
3. Продолжить миграцию компонентов

