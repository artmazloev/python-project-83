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
    def _get_read_cursor(self):
        """
        Context manager for read-only database operations.
        Does not commit or rollback as read operations don't need it.
        
        Yields:
            A DictCursor instance for database read operations.
        """
        if self.conn is None or self.conn.closed:
            self.conn = psycopg2.connect(self.db)
        
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            yield cur

    @contextmanager
    def _get_write_cursor(self):
        """
        Context manager for write database operations.
        Handles commit/rollback for write operations.
        
        Yields:
            A DictCursor instance for database write operations.
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

    @contextmanager
    def transaction(self):
        """
        Context manager for managing database transactions.
        Allows multiple operations within a single transaction.
        
        Yields:
            A DictCursor instance for database operations within transaction.
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
            with their most recent check data.
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
        with self._get_read_cursor() as cur:
            cur.execute(query)
            return [dict(row) for row in cur.fetchall()]
 
    def exist_url_id(self, url_id):
        """
        Check if a URL with the given ID exists.
        
        Args:
            url_id: The ID of the URL to check
            
        Returns:
            dict: The URL record as a dictionary if found, None otherwise
        """
        query = """
            SELECT id, name, created_at 
            FROM urls 
            WHERE id = %s
        """
        with self._get_read_cursor() as cur:
            cur.execute(query, (url_id,))
            result = cur.fetchone()
            return dict(result) if result else None
 
    def find_url_name(self, name):
        """
        Find a URL by its name and return its ID.
        
        Args:
            name (str): The URL name to search for
            
        Returns:
            int: The URL ID if found, None otherwise
        """
        query = "SELECT id FROM urls WHERE name = %s"
        with self._get_read_cursor() as cur:
            cur.execute(query, (name,))
            result = cur.fetchone()
            return result['id'] if result else None
 
    def save_url(self, url):
        """
        Save a new URL to the database.
        Uses database DEFAULT for created_at timestamp.
        
        Args:
            url (str): The URL to save
            
        Returns:
            int: The ID of the newly created URL record
        """
        query = """
            INSERT INTO urls (name)
            VALUES (%s)
            RETURNING id
        """
        with self._get_write_cursor() as cur:
            cur.execute(query, (url,))
            result = cur.fetchone()
            return result['id']
 
    def save_url_check(self, content):
        """
        Save URL check information to the database.
        Uses database DEFAULT for created_at timestamp.
        
        Args:
            content (dict): Dictionary containing check information with keys:
                    - url_id (int): The URL ID being checked
                    - status_code (int): HTTP status code
                    - h1 (str): H1 content if any
                    - title (str): Page title if any
                    - description (str): Page description if any
        """
        query = """
            INSERT INTO url_checks (
                url_id, status_code, h1, title, description
            ) VALUES %s
        """
        check_info = [(
            content['url_id'],
            content['status_code'],
            content['h1'],
            content['title'],
            content['description']
        )]
        
        with self._get_write_cursor() as cur:
            execute_values(cur, query, check_info)
 
    def get_content_check(self, url_id):
        """
        Retrieve all check records for a specific URL.
        
        Args:
            url_id (int): The ID of the URL to get checks for
            
        Returns:
            List[dict]: List of dictionaries containing check information
                       ordered by most recent first
        """
        query = """
            SELECT id, url_id, status_code, h1, title, description, created_at
            FROM url_checks
            WHERE url_id = %s
            ORDER BY id DESC
        """
        with self._get_read_cursor() as cur:
            cur.execute(query, (url_id,))
            return [dict(row) for row in cur.fetchall()]
 
    def __enter__(self):
        """Support for context manager protocol."""
        return self
 
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure connection is closed when exiting context."""
        self._close()