# Выдача прав пользователю вместо отключения RLS

## Почему это лучше?

✅ **Безопаснее:** RLS остается включенным для других пользователей  
✅ **Гибче:** Можно настроить права на каждую таблицу отдельно  
✅ **Правильнее:** Соответствует best practices PostgreSQL  
✅ **Контролируемо:** Можно видеть, кто имеет доступ к каким данным

## Что нужно сделать

### Вариант 1: Через Supabase Dashboard (РЕКОМЕНДУЕТСЯ)

1. **Откройте Supabase Dashboard:**
   - https://supabase.com/dashboard
   - Выберите проект `uyymukgccsqzagpusswm`

2. **Откройте SQL Editor:**
   - SQL Editor → New Query

3. **Выполните SQL из файла `grant_permissions.sql`**

4. **Проверьте результат:**
   Выполните запрос для проверки прав:

```sql
SELECT 
    grantee,
    table_schema,
    table_name,
    privilege_type
FROM information_schema.role_table_grants
WHERE grantee = 'gen_user'
ORDER BY table_schema, table_name, privilege_type;
```

### Вариант 2: Через Supabase CLI

```bash
supabase db execute -f grant_permissions.sql
```

## Какие права выдаются?

1. **USAGE на схему public** - доступ к схеме
2. **SELECT, INSERT, UPDATE, DELETE** на все таблицы - полный доступ к данным
3. **USAGE, SELECT на последовательности** - для автоинкремента
4. **DEFAULT PRIVILEGES** - автоматическая выдача прав на новые таблицы

## Если RLS все еще блокирует

Если после выдачи прав RLS все еще блокирует доступ, нужно:

### Вариант A: Создать политику RLS для gen_user

```sql
-- Пример для таблицы profiles
CREATE POLICY "gen_user_full_access" ON public.profiles
    FOR ALL
    TO gen_user
    USING (true)
    WITH CHECK (true);
```

### Вариант B: Временно отключить RLS только для gen_user

```sql
-- Создать роль с обходом RLS
ALTER USER gen_user WITH BYPASSRLS;
```

⚠️ **Внимание:** `BYPASSRLS` обходит все RLS политики. Используйте осторожно!

## Рекомендуемый подход

1. **Сначала выдайте права** (SQL из `grant_permissions.sql`)
2. **Протестируйте** - может быть этого достаточно
3. **Если RLS все еще блокирует** - используйте `BYPASSRLS` или создайте политики

## Проверка после выдачи прав

```sql
-- Проверить права пользователя
SELECT 
    grantee,
    table_schema,
    table_name,
    privilege_type
FROM information_schema.role_table_grants
WHERE grantee = 'gen_user';

-- Проверить, обходит ли пользователь RLS
SELECT 
    rolname,
    rolbypassrls
FROM pg_roles
WHERE rolname = 'gen_user';
```

