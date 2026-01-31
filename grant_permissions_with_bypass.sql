-- ============================================================
-- ВЫДАЧА ПРАВ + ОБХОД RLS ДЛЯ gen_user
-- ============================================================
-- Комплексное решение: выдаем права И разрешаем обход RLS
-- Это позволяет gen_user работать с данными, не отключая RLS глобально
-- ============================================================

-- 1. Выдать права на схему
GRANT USAGE ON SCHEMA public TO gen_user;
GRANT ALL ON SCHEMA public TO gen_user;

-- 2. Выдать права на все таблицы
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO gen_user;

-- 3. Выдать права на последовательности
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO gen_user;

-- 4. Выдать права на будущие таблицы
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO gen_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO gen_user;

-- 5. Разрешить обход RLS для gen_user (ВАЖНО!)
ALTER USER gen_user WITH BYPASSRLS;

-- 6. Специфичные права на таблицы (если нужны)
GRANT ALL PRIVILEGES ON TABLE public.profiles TO gen_user;
GRANT ALL PRIVILEGES ON TABLE public.user_roles TO gen_user;
GRANT ALL PRIVILEGES ON TABLE public.lesson_content TO gen_user;
GRANT ALL PRIVILEGES ON TABLE public.practical_materials TO gen_user;
GRANT ALL PRIVILEGES ON TABLE public.student_progress TO gen_user;
GRANT ALL PRIVILEGES ON TABLE public.invitation_codes TO gen_user;
GRANT ALL PRIVILEGES ON TABLE public.waitlist TO gen_user;

-- 7. Если есть таблица auth.users
GRANT SELECT ON TABLE auth.users TO gen_user;

-- Проверить результат
SELECT 
    rolname,
    rolbypassrls,
    rolcanlogin
FROM pg_roles
WHERE rolname = 'gen_user';

SELECT 
    grantee,
    table_schema,
    table_name,
    privilege_type
FROM information_schema.role_table_grants
WHERE grantee = 'gen_user'
ORDER BY table_schema, table_name, privilege_type;

