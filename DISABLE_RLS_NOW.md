# Отключение RLS - Инструкция

## ⚠️ ВРЕМЕННОЕ РЕШЕНИЕ

Это временное решение для быстрого запуска.  
В продакшене рекомендуется использовать SECURITY DEFINER функции или настроить правильные RLS политики.

## Шаг 1: Войти в панель управления Timeweb

1. Откройте https://timeweb.com
2. Войдите в свой аккаунт
3. Перейдите в раздел **Облачные базы данных** или **Базы данных**

## Шаг 2: Открыть SQL консоль

1. Найдите базу данных `db_21day`
2. Откройте **SQL консоль** или **Query Editor**
3. Убедитесь, что подключены к базе `db_21day`

## Шаг 3: Выполнить SQL команды

Скопируйте и выполните следующие команды:

```sql
-- ВРЕМЕННОЕ РЕШЕНИЕ: Отключение RLS для backend доступа
-- ВНИМАНИЕ: Это временное решение для быстрого запуска.
-- В продакшене рекомендуется использовать SECURITY DEFINER функции
-- или настроить правильные RLS политики.

-- Отключить RLS для всех таблиц
ALTER TABLE IF EXISTS public.profiles DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.user_roles DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.lesson_content DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.practical_materials DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.student_progress DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.invitation_codes DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.waitlist DISABLE ROW LEVEL SECURITY;
```

## Шаг 4: Проверить результат

Выполните запрос для проверки:

```sql
SELECT 
    schemaname,
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables 
WHERE schemaname = 'public' 
  AND tablename IN (
    'profiles',
    'user_roles',
    'lesson_content',
    'practical_materials',
    'student_progress',
    'invitation_codes',
    'waitlist'
  )
ORDER BY tablename;
```

Все таблицы должны показать `rls_enabled = false` (или `f`)

## Шаг 5: Протестировать backend

После отключения RLS, backend должен успешно читать данные.

Проверьте логи backend:
```bash
ssh root@195.133.63.34
journalctl -u 21day-api -n 50
```

Или протестируйте API:
```bash
curl https://21day.club/api/health
```

## Что дальше?

После отключения RLS:
1. ✅ Backend сможет читать данные
2. ✅ API endpoints заработают
3. ⏳ Продолжить миграцию компонентов на API
4. ⏳ Пересобрать и развернуть фронтенд

