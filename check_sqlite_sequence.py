"""Проверка таблицы sqlite_sequence"""
import sqlite3

conn = sqlite3.connect('chatlist.db')
cursor = conn.cursor()

# Получаем все таблицы
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()
print("Таблицы в БД:")
for table in tables:
    print(f"  - {table[0]}")

# Проверяем sqlite_sequence
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sqlite_sequence'")
seq = cursor.fetchone()
print(f"\nsqlite_sequence существует: {seq is not None}")

if seq:
    cursor.execute("SELECT * FROM sqlite_sequence")
    rows = cursor.fetchall()
    print("\nСодержимое sqlite_sequence:")
    for row in rows:
        print(f"  Таблица: {row[0]}, Последний ID: {row[1]}")

conn.close()





