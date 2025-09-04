# page_analyzer/db.py

import os
from contextlib import contextmanager
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import DictCursor

# Загружаем URL базы данных из переменных окружения
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

# Инициализируем пул соединений один раз при загрузке модуля
try:
    pool = SimpleConnectionPool(minconn=1, maxconn=10, dsn=DATABASE_URL)
except psycopg2.OperationalError as e:
    raise RuntimeError(f"Could not connect to the database: {e}") from e


@contextmanager
def get_connection():
    """
    Контекстный менеджер для получения соединения из пула.
    Гарантирует, что соединение будет возвращено в пул после использования.
    """
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)


def get_content():
    """
    Получает все URL с данными последней проверки.
    """
    query = """
        SELECT DISTINCT ON (urls.id)
            urls.id,
            urls.name,
            url_checks.created_at,
            url_checks.status_code
        FROM urls
        LEFT JOIN url_checks ON urls.id = url_checks.url_id
        ORDER BY urls.id DESC, url_checks.created_at DESC;
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query)
            return [dict(row) for row in cur.fetchall()]


def find_url_name(name):
    """
    Находит URL по имени.
    """
    query = "SELECT id FROM urls WHERE name = %s;"
    with get_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query, (name,))
            result = cur.fetchone()
            return result['id'] if result else None


def save_url(url):
    """
    Сохраняет новый URL.
    """
    query = "INSERT INTO urls (name) VALUES (%s) RETURNING id;"
    with get_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query, (url,))
            result = cur.fetchone()
            conn.commit()
            return result['id']


def exist_url_id(url_id):
    """
    Находит URL по id.
    """
    query = "SELECT id, name, created_at FROM urls WHERE id = %s;"
    with get_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query, (url_id,))
            result = cur.fetchone()
            return dict(result) if result else None


def save_url_check(content):
    """
    Сохраняет результат проверки сайта.
    """
    query = """
        INSERT INTO url_checks (url_id, status_code, h1, title, description)
        VALUES (%s, %s, %s, %s, %s);
    """
    check_info = (
        content['url_id'],
        content['status_code'],
        content['h1'],
        content['title'],
        content['description']
    )
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, check_info)
            conn.commit()


def get_content_check(url_id):
    """
    Получает все проверки для конкретного URL.
    """
    query = """
        SELECT id, url_id, status_code, h1, title, description, created_at
        FROM url_checks
        WHERE url_id = %s
        ORDER BY id DESC;
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query, (url_id,))
            return [dict(row) for row in cur.fetchall()]


def close_pool():
    """
    Закрывает все соединения в пуле.
    Полезно для чистого завершения работы приложения.
    """
    pool.closeall()
