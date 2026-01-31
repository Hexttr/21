-- ============================================================
-- ВЫДАЧА ПРАВ ПОЛЬЗОВАТЕЛЮ gen_user
-- ============================================================
-- Это более безопасное решение, чем отключение RLS.
-- RLS остается включенным, но gen_user получает права на доступ к данным.
-- ============================================================

-- Выдать права на схему public (если нужно)
GRANT USAGE ON SCHEMA public TO gen_user;
GRANT ALL ON SCHEMA public TO gen_user;

-- Выдать права на все таблицы
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO gen_user;

-- Выдать права на последовательности (для автоинкремента)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO gen_user;

-- Выдать права на будущие таблицы (чтобы не нужно было выдавать каждый раз)
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO gen_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO gen_user;

-- Специфичные права на конкретные таблицы (если нужны дополнительные права)
GRANT ALL PRIVILEGES ON TABLE public.profiles TO gen_user;
GRANT ALL PRIVILEGES ON TABLE public.user_roles TO gen_user;
GRANT ALL PRIVILEGES ON TABLE public.lesson_content TO gen_user;
GRANT ALL PRIVILEGES ON TABLE public.practical_materials TO gen_user;
GRANT ALL PRIVILEGES ON TABLE public.student_progress TO gen_user;
GRANT ALL PRIVILEGES ON TABLE public.invitation_codes TO gen_user;
GRANT ALL PRIVILEGES ON TABLE public.waitlist TO gen_user;

-- Если есть таблица auth.users (для чтения)
GRANT SELECT ON TABLE auth.users TO gen_user;

-- Проверить текущие права пользователя
SELECT 
    grantee,
    table_schema,
    table_name,
    privilege_type
FROM information_schema.role_table_grants
WHERE grantee = 'gen_user'
ORDER BY table_schema, table_name, privilege_type;

