import datetime
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import DictCursor, execute_values


class Database:
    """
    Optimized class for interacting with a PostgreSQL database using psycopg2.
 
    Attributes:
    - database (str): The connection string for the PostgreSQL database.
    - conn (psycopg2.connection): The database connection object.

    Methods:
    - get_content(): Retrieve content from the database.
    - exist_url_id(id): Check if a given URL id exists in the database.
    - find_url_name(name): Find the URL name in the database.
    - save_url(url): Save a new URL in the database.
    - save_url_check(content): Save URL check information in the database.
    - get_content_check(url_id): Retrieve URL check content from the database.
    """
 
    def __init__(self, database):
        """Initialize with database connection string."""
        self.db = database
        self.conn = None
 
    @contextmanager
    def _get_cursor(self):
        """
        Context manager for handling database cursor
        with automatic connection management.
        
        Yields:
            A DictCursor instance for database operations.
        """
        if self.conn is None or self.conn.closed:
            self.conn = psycopg2.connect(self.db)
        
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            try:
                yield cur
                self.conn.commit()
            except Exception as e:
                self.conn.rollback()
                raise e
 
    def _close(self):
        """Close the database connection if it exists and is open."""
        if self.conn is not None and not self.conn.closed:
            self.conn.close()
        self.conn = None
 
    def get_content(self):
        """
        Retrieve content from the database with most recent check information.
        
        Returns:
            List of dictionaries containing URL information
            with their most recent check.
        """
        query = """
            SELECT DISTINCT ON (urls.id)
                urls.id,
                urls.name,
                url_checks.created_at,
                url_checks.status_code
            FROM urls
            LEFT JOIN url_checks ON urls.id = url_checks.url_id
            ORDER BY urls.id DESC, url_checks.created_at DESC
        """
        with self._get_cursor() as cur:
            cur.execute(query)
            return [dict(row) for row in cur.fetchall()]
 
    def exist_url_id(self, url_id):
        """
        Check if a URL with the given ID exists.
        
        Args:
            url_id: The ID of the URL to check
            
        Returns:
            The URL record as a dictionary if found, None otherwise
        """
        with self._get_cursor() as cur:
            cur.execute("SELECT * FROM urls WHERE id = %s", (url_id,))
            return cur.fetchone()
 
    def find_url_name(self, name):
        """
        Find a URL by its name and return its ID.
        
        Args:
            name: The URL name to search for
            
        Returns:
            The URL ID if found, None otherwise
        """
        with self._get_cursor() as cur:
            cur.execute("SELECT id FROM urls WHERE name = %s", (name,))
            result = cur.fetchone()
            return result[0] if result else None
 
    def save_url(self, url):
        """
        Save a new URL to the database.
        
        Args:
            url: The URL to save
            
        Returns:
            The ID of the newly created URL record
        """
        query = """
            INSERT INTO urls (name, created_at)
            VALUES (%s, %s)
            RETURNING id
        """
        with self._get_cursor() as cur:
            cur.execute(query, (url, datetime.date.today()))
            return cur.fetchone()[0]
 
    def save_url_check(self, content):
        """
        Save URL check information to the database.
        
        Args:
            content: Dictionary containing check information with keys:
                    - url_id: The URL ID being checked
                    - status_code: HTTP status code
                    - h1: H1 content if any
                    - title: Page title if any
                    - description: Page description if any
        """
        query = """
            INSERT INTO url_checks (
                url_id, status_code, h1, title, description, created_at
            ) VALUES %s
        """
        check_info = [(
            content['url_id'],
            content['status_code'],
            content['h1'],
            content['title'],
            content['description'],
            datetime.date.today()
        )]
        
        with self._get_cursor() as cur:
            execute_values(cur, query, check_info)
 
    def get_content_check(self, url_id):
        """
        Retrieve all check records for a specific URL.
        
        Args:
            url_id: The ID of the URL to get checks for
            
        Returns:
            List of dictionaries containing check information
        """
        query = """
            SELECT * FROM url_checks
            WHERE url_id = %s
            ORDER BY id DESC
        """
        with self._get_cursor() as cur:
            cur.execute(query, (url_id,))
            return cur.fetchall()
 
    def __enter__(self):
        """Support for context manager protocol."""
        return self
 
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure connection is closed when exiting context."""
        self._close()
