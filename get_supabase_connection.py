#!/usr/bin/env python3
"""Get Supabase PostgreSQL connection details"""

# Supabase project details
SUPABASE_PROJECT_ID = "uyymukgccsqzagpusswm"
SUPABASE_URL = "https://uyymukgccsqzagpusswm.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV5eW11a2djY3NxemFncHVzc3dtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgxNTIzMDksImV4cCI6MjA4MzcyODMwOX0.IkUJbJPXO5zNuB-9oEZs0v38zHYrkoSc1ofniHSJM9M"

print("=" * 60)
print("SUPABASE PROJECT INFORMATION")
print("=" * 60)
print()
print(f"Project ID: {SUPABASE_PROJECT_ID}")
print(f"URL: {SUPABASE_URL}")
print()
print("=" * 60)
print("POSTGRESQL CONNECTION")
print("=" * 60)
print()
print("Supabase использует PostgreSQL под капотом.")
print("Для подключения к базе данных нужно:")
print()
print("1. Получить connection string из панели Supabase:")
print("   - Settings -> Database -> Connection string")
print("   - Или использовать формат:")
print("   postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres")
print()
print("2. Или использовать прямую ссылку:")
print("   postgresql://postgres.[project-ref]:[password]@db.[project-ref].supabase.co:5432/postgres")
print()
print("=" * 60)
print("NEXT STEPS")
print("=" * 60)
print()
print("1. Получить connection string из Supabase Dashboard")
print("2. Обновить backend/.env с новым connection string")
print("3. Продолжить миграцию компонентов на API")
print()

