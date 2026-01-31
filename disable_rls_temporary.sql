-- ============================================================
-- ВРЕМЕННОЕ РЕШЕНИЕ: Отключение RLS для backend доступа
-- ============================================================
-- ВНИМАНИЕ: Это временное решение для быстрого запуска.
-- В продакшене рекомендуется использовать SECURITY DEFINER функции
-- или настроить правильные RLS политики.
-- ============================================================

-- Отключить RLS для всех таблиц, к которым нужен доступ
ALTER TABLE IF EXISTS public.profiles DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.user_roles DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.lesson_content DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.practical_materials DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.student_progress DISABLE ROW LEVEL SECURITY;

-- Отключить RLS для таблиц, которые могут существовать
ALTER TABLE IF EXISTS public.invitation_codes DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.waitlist DISABLE ROW LEVEL SECURITY;

-- Проверить статус RLS
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

