# Инструкция: Временное отключение RLS

## ⚠️ ВНИМАНИЕ
Это **ВРЕМЕННОЕ** решение для быстрого запуска проекта.  
В продакшене рекомендуется использовать SECURITY DEFINER функции или настроить правильные RLS политики.

## Проблема
Пользователь `gen_user` не имеет права `CONNECT` к базе данных `db_21day` с сервера.

## Варианты решения

### Вариант 1: Через панель управления Timeweb (РЕКОМЕНДУЕТСЯ)

1. Войдите в панель управления Timeweb
2. Перейдите в раздел **Базы данных** → **PostgreSQL**
3. Выберите базу данных `db_21day`
4. Откройте **SQL Console** или **Query Editor**
5. Выполните SQL команды из файла `disable_rls_temporary.sql`:

```sql
-- Отключить RLS для всех таблиц
ALTER TABLE IF EXISTS public.profiles DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.user_roles DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.lesson_content DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.practical_materials DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.student_progress DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.invitation_codes DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.waitlist DISABLE ROW LEVEL SECURITY;
```

6. Проверьте результат:

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

Все таблицы должны показать `rls_enabled = false`

---

### Вариант 2: Запросить права у поддержки Timeweb

1. Обратитесь в поддержку Timeweb
2. Попросите предоставить пользователю `gen_user` права:
   - `CONNECT` на базу данных `db_21day`
   - Возможность выполнять `ALTER TABLE` команды

3. После получения прав выполните:
```bash
python disable_rls.py
```

---

### Вариант 3: Создать admin endpoint в backend

Создать специальный endpoint в backend для выполнения SQL (только для админов):

```javascript
// backend/routes/admin.js
router.post('/execute-sql', requireAdmin, async (req, res) => {
  // Execute SQL commands
  // WARNING: Only for trusted admins!
});
```

---

## После отключения RLS

1. **Протестируйте доступ:**
   ```bash
   python test_db_access_now.py
   ```

2. **Проверьте работу backend:**
   - Backend должен успешно читать данные
   - API endpoints должны работать

3. **Помните:** Это временное решение!
   - Запланируйте переход на SECURITY DEFINER функции
   - Или настройте правильные RLS политики

---

## Проверка работы

После отключения RLS backend должен успешно:
- ✅ Читать профили пользователей
- ✅ Читать уроки
- ✅ Читать прогресс студентов
- ✅ Обновлять данные

Если что-то не работает, проверьте логи backend:
```bash
ssh root@195.133.63.34
journalctl -u 21day-api -n 50
```

