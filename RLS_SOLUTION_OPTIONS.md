# Варианты решения проблемы RLS (Row Level Security)

## Проблема
Backend не может читать данные из PostgreSQL из-за RLS политик, которые были настроены для Supabase и требуют `auth.uid()`.

## Варианты решения

### Вариант 1: Отключить RLS для backend пользователя (РЕКОМЕНДУЕТСЯ)
**Сложность:** Низкая  
**Безопасность:** Средняя (нужно правильно настроить права)  
**Время:** 5-10 минут

**Шаги:**
```sql
-- Отключить RLS для всех таблиц для пользователя gen_user
ALTER TABLE public.profiles DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_roles DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.lesson_content DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.practical_materials DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.student_progress DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.invitation_codes DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.waitlist DISABLE ROW LEVEL SECURITY;
```

**Плюсы:**
- Быстро и просто
- Backend сразу получит доступ ко всем данным
- Не требует изменений в коде

**Минусы:**
- Меньше безопасности на уровне БД
- Нужно контролировать доступ на уровне приложения

---

### Вариант 2: Создать SECURITY DEFINER функции
**Сложность:** Средняя  
**Безопасность:** Высокая  
**Время:** 20-30 минут

**Идея:** Создать функции с правами суперпользователя, которые обходят RLS.

**Шаги:**
```sql
-- Создать функцию для чтения профилей
CREATE OR REPLACE FUNCTION public.get_user_profiles()
RETURNS TABLE (
  user_id uuid,
  email text,
  name text,
  blocked boolean,
  invitation_code_id uuid
) 
SECURITY DEFINER
SET search_path = public
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT p.user_id, p.email, p.name, p.blocked, p.invitation_code_id
  FROM public.profiles p;
END;
$$;

-- Дать права backend пользователю
GRANT EXECUTE ON FUNCTION public.get_user_profiles() TO gen_user;
```

**Плюсы:**
- Высокая безопасность
- RLS остается включенным
- Контролируемый доступ через функции

**Минусы:**
- Нужно создать функции для каждой операции
- Больше кода в БД
- Нужно обновить backend для использования функций

---

### Вариант 3: Использовать service role (если доступен)
**Сложность:** Низкая  
**Безопасность:** Высокая  
**Время:** 5 минут

**Идея:** Если у вас есть service role с правами суперпользователя, использовать его для backend.

**Шаги:**
1. Получить credentials для service role
2. Обновить connection string в backend
3. Service role автоматически обходит RLS

**Плюсы:**
- Просто
- Безопасно
- Не требует изменений в БД

**Минусы:**
- Нужен доступ к service role
- Может быть недоступен в Timeweb

---

### Вариант 4: Изменить RLS политики для backend пользователя
**Сложность:** Высокая  
**Безопасность:** Высокая  
**Время:** 30-60 минут

**Идея:** Создать специальные политики, которые разрешают доступ для backend пользователя.

**Шаги:**
```sql
-- Создать роль для backend
CREATE ROLE backend_user;

-- Изменить политики
CREATE POLICY "backend_access" ON public.profiles
  FOR ALL
  TO backend_user
  USING (true)
  WITH CHECK (true);

-- Назначить роль пользователю
GRANT backend_user TO gen_user;
```

**Плюсы:**
- Гибкость
- Можно настроить доступ к конкретным таблицам
- RLS остается включенным

**Минусы:**
- Сложнее настроить
- Нужно знать структуру всех политик

---

### Вариант 5: Создать отдельную схему без RLS
**Сложность:** Средняя  
**Безопасность:** Средняя  
**Время:** 15-20 минут

**Идея:** Создать новую схему для backend без RLS, скопировать туда данные.

**Шаги:**
```sql
-- Создать схему
CREATE SCHEMA backend_api;

-- Скопировать таблицы
CREATE TABLE backend_api.profiles AS SELECT * FROM public.profiles;

-- Дать права
GRANT ALL ON SCHEMA backend_api TO gen_user;
GRANT ALL ON ALL TABLES IN SCHEMA backend_api TO gen_user;
```

**Плюсы:**
- Изоляция данных
- Не влияет на существующие таблицы

**Минусы:**
- Дублирование данных
- Нужна синхронизация
- Больше места в БД

---

## Рекомендация

**Для быстрого решения:** Вариант 1 (отключить RLS)  
**Для продакшена:** Вариант 2 (SECURITY DEFINER функции) или Вариант 3 (service role)

## Следующие шаги

1. Выбрать вариант
2. Выполнить SQL команды
3. Протестировать доступ из backend
4. Обновить документацию

