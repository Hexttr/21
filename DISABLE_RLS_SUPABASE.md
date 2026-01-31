# Отключение RLS через Supabase

## Варианты решения

### Вариант 1: Supabase Dashboard (РЕКОМЕНДУЕТСЯ - Самый простой)

1. **Откройте Supabase Dashboard:**
   - https://supabase.com/dashboard
   - Войдите в аккаунт
   - Выберите проект `uyymukgccsqzagpusswm`

2. **Откройте SQL Editor:**
   - В левом меню найдите **SQL Editor**
   - Нажмите **New Query**

3. **Выполните SQL команды:**
   Скопируйте и вставьте следующие команды:

```sql
-- ВРЕМЕННОЕ РЕШЕНИЕ: Отключение RLS для backend доступа
ALTER TABLE IF EXISTS public.profiles DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.user_roles DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.lesson_content DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.practical_materials DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.student_progress DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.invitation_codes DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.waitlist DISABLE ROW LEVEL SECURITY;
```

4. **Нажмите Run** (или Ctrl+Enter)

5. **Проверьте результат:**
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

---

### Вариант 2: Supabase CLI

Если у вас установлен Supabase CLI:

```bash
# 1. Установить Supabase CLI (если не установлен)
npm install -g supabase

# 2. Войти в Supabase
supabase login

# 3. Связать проект
supabase link --project-ref uyymukgccsqzagpusswm

# 4. Выполнить SQL
supabase db execute -f disable_rls_temporary.sql
```

---

### Вариант 3: Через API (если есть service role key)

Если у вас есть Service Role Key из Supabase Dashboard:

```python
# Можно использовать Supabase Python client
from supabase import create_client, Client

url = "https://uyymukgccsqzagpusswm.supabase.co"
service_key = "your-service-role-key"  # Из Settings -> API

supabase: Client = create_client(url, service_key)

# Выполнить SQL через RPC (если есть функция)
# Или использовать прямой PostgreSQL connection
```

---

## Рекомендация

**Используйте Вариант 1 (Supabase Dashboard)** - это самый простой и быстрый способ.

После отключения RLS:
1. Backend сможет читать данные
2. API endpoints заработают
3. Можно продолжить миграцию компонентов

