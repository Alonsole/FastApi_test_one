import os
from dotenv import load_dotenv


# Загрузка переменных окружений
dotenv_file = '../.env'
load_dotenv(dotenv_file)


# Настройки подключения к базе данных
DB_HOST = os.environ.get("POSTGRES_DBHOST", "127.0.0.1")
DB_PORT = os.environ.get("POSTGRES_PORT", "5432")
DB_NAME = os.environ.get("POSTGRES_DBNAME", "postgres")
DB_USER = os.environ.get("POSTGRES_USER", "postgres")
DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "1234")


PG_DSN = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}'

# print(PG_DSN)  # Проверка успешной загрузки .env