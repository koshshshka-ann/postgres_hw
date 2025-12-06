import os
import psycopg2
from psycopg2 import sql, Error
from dotenv import load_dotenv
from typing import List, Tuple, Optional
from datetime import datetime


class PostgresDriver:
    """Драйвер для работы с PostgreSQL"""

    def __init__(self):
        """Инициализация драйвера"""
        load_dotenv()
        self.connection = None

    def connect(self) -> bool:
        """
        Подключение к базе данных

        Returns:
            bool: True если подключение успешно, False в противном случае
        """
        try:
            self.connection = psycopg2.connect(
                host=os.getenv("DB_HOST", "localhost"),
                port=os.getenv("DB_PORT", "5432"),
                dbname=os.getenv("DB_NAME", "test"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD", "")
            )
            return True
        except Error as e:
            print(f"❌ Ошибка подключения: {e}")
            return False

    def disconnect(self) -> None:
        """Закрытие соединения с базой данных"""
        if self.connection:
            self.connection.close()
            self.connection = None

    def __enter__(self):
        """Контекстный менеджер для автоматического подключения"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Контекстный менеджер для автоматического отключения"""
        self.disconnect()

    def create_tables(self) -> bool:
        """
        Создание таблиц users и orders

        Returns:
            bool: True если таблицы созданы успешно
        """
        try:
            with self.connection.cursor() as cursor:
                # Создаем таблицу users
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id   SERIAL PRIMARY KEY,
                        name TEXT NOT NULL,
                        age  INTEGER CHECK (age >= 0)
                    );
                """)

                # Создаем таблицу orders
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS orders (
                        id         SERIAL PRIMARY KEY,
                        user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        amount     NUMERIC(10,2) NOT NULL CHECK (amount >= 0),
                        created_at TIMESTAMP DEFAULT NOW()
                    );
                """)

                self.connection.commit()
                return True

        except Error as e:
            self.connection.rollback()
            print(f"❌ Ошибка при создании таблиц: {e}")
            return False

    def add_user(self, name: str, age: int) -> Optional[int]:
        """
        Добавление нового пользователя

        Args:
            name: Имя пользователя
            age: Возраст пользователя

        Returns:
            int: ID созданного пользователя или None в случае ошибки
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (name, age) VALUES (%s, %s) RETURNING id;",
                    (name, age)
                )
                user_id = cursor.fetchone()[0]
                self.connection.commit()
                return user_id

        except Error as e:
            self.connection.rollback()
            print(f"❌ Ошибка при добавлении пользователя: {e}")
            return None

    def add_order(self, user_id: int, amount: float) -> Optional[int]:
        """
        Добавление нового заказа

        Args:
            user_id: ID пользователя
            amount: Сумма заказа

        Returns:
            int: ID созданного заказа или None в случае ошибки
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO orders (user_id, amount) 
                       VALUES (%s, %s) RETURNING id;""",
                    (user_id, amount)
                )
                order_id = cursor.fetchone()[0]
                self.connection.commit()
                return order_id

        except Error as e:
            self.connection.rollback()
            print(f"❌ Ошибка при добавлении заказа: {e}")
            return None

    def get_user_totals(self) -> List[Tuple[str, float]]:
        """
        Получение суммы заказов по каждому пользователю

        Returns:
            List[Tuple[str, float]]: Список кортежей (имя_пользователя, сумма_заказов)
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        u.name,
                        COALESCE(SUM(o.amount), 0) as total_amount
                    FROM users u
                    LEFT JOIN orders o ON u.id = o.user_id
                    GROUP BY u.id, u.name
                    ORDER BY total_amount DESC, u.name;
                """)
                return cursor.fetchall()

        except Error as e:
            print(f"❌ Ошибка при получении статистики: {e}")
            return []

    def get_all_users(self) -> List[Tuple[int, str, int]]:
        """
        Получение всех пользователей

        Returns:
            List[Tuple[int, str, int]]: Список всех пользователей (id, name, age)
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT id, name, age FROM users ORDER BY id;")
                return cursor.fetchall()
        except Error as e:
            print(f"❌ Ошибка при получении пользователей: {e}")
            return []

    def get_user_orders(self, user_id: int) -> List[Tuple[int, float, datetime]]:
        """
        Получение всех заказов пользователя

        Args:
            user_id: ID пользователя

        Returns:
            List[Tuple[int, float, datetime]]: Список заказов (id, amount, created_at)
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id, amount, created_at FROM orders WHERE user_id = %s ORDER BY created_at;",
                    (user_id,)
                )
                return cursor.fetchall()
        except Error as e:
            print(f"❌ Ошибка при получении заказов пользователя: {e}")
            return []

    def delete_user(self, user_id: int) -> bool:
        """
        Удаление пользователя (с каскадным удалением заказов)

        Args:
            user_id: ID пользователя

        Returns:
            bool: True если удаление успешно
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE id = %s;", (user_id,))
                self.connection.commit()
                return cursor.rowcount > 0
        except Error as e:
            self.connection.rollback()
            print(f"❌ Ошибка при удалении пользователя: {e}")
            return False

    def clear_tables(self) -> bool:
        """
        Очистка всех таблиц (удаление всех данных)

        Returns:
            bool: True если очистка успешна
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("DELETE FROM orders;")
                cursor.execute("DELETE FROM users;")
                self.connection.commit()
                return True
        except Error as e:
            self.connection.rollback()
            print(f"❌ Ошибка при очистке таблиц: {e}")
            return False
