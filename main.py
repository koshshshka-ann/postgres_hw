import os
import psycopg2
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Подключаемся к базе данных
try:
    connection = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

    print("✅ Подключение к PostgreSQL успешно!")

    # Создаем курсор для выполнения SQL-запросов
    cursor = connection.cursor()

    # Выполняем SELECT запрос
    cursor.execute("SELECT id, name, age FROM users;")

    # Получаем все строки
    rows = cursor.fetchall()

    print(f"\n📊 Найдено {len(rows)} пользователей:\n")

    # Выводим результат
    for row in rows:
        print(f"ID: {row[0]}, Имя: {row[1]}, Возраст: {row[2]}")

    cursor.close()

except (Exception, psycopg2.Error) as error:
    print(f"❌ Ошибка при работе с PostgreSQL: {error}")

finally:
    # Закрываем соединение
    if connection:
        connection.close()
        print("\n🔒 Соединение с PostgreSQL закрыто")
