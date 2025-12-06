# Проект: Подключение Python к PostgreSQL

## Описание
Простой скрипт для подключения к базе данных PostgreSQL и чтения данных из таблицы users.

## Предварительные требования
- Установленный PostgreSQL с pgAdmin
- Созданная база данных `test` с таблицей `users`
- Python 3.8+

## Установка и запуск

### 1. Клонирование и настройка
```bash
# Клонируйте репозиторий
git clone <ваш-репозиторий>
cd <папка-проекта>

# Создайте виртуальное окружение
python -m venv venv

# Активируйте окружение
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt
```

### 2. Настройка базы данных
1. Откройте pgAdmin
2. Создайте базу данных `test`
3. Создайте таблицу:
```sql
CREATE TABLE users (
    id   SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    age  INT CHECK (age >= 0)
);
```
4. Добавьте тестовые данные через интерфейс pgAdmin

### 3. Настройка подключения
```bash
# Скопируйте шаблон настроек
cp .env.example .env

# Отредактируйте .env файл, указав свои данные:
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=test
# DB_USER=postgres
# DB_PASSWORD=ваш_пароль
```

### 4. Запуск
```bash
python main.py
```

## Ожидаемый результат
При успешном выполнении скрипт выведет список пользователей из таблицы `users`.

## Структура проекта
- `main.py` - основной скрипт
- `requirements.txt` - зависимости Python
- `.env.example` - шаблон настроек подключения
- `README.md` - эта инструкция

## Примечания
- Файл `.env` не включен в репозиторий по соображениям безопасности
- Убедитесь, что PostgreSQL сервер запущен перед выполнением скрипта
