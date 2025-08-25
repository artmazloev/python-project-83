from urllib.parse import urlparse
from typing import Dict

import requests
import validators
from bs4 import BeautifulSoup


class URLValidationErrors(Exception):
    """Base class for URL validation errors with optional context."""
    def __init__(self, message: str = "", url: str | None = None):
        details = f" URL: {url}" if url else ""
        super().__init__(f"{message}{details}")
        self.url = url


class URLNotValid(URLValidationErrors):
    """Raised when a URL fails validation (syntax/scheme/host)."""


class URLTooLong(URLValidationErrors):
    """Raised when a URL length exceeds configured maximum."""


def check_url(url: str) -> None:
    """Validate URL syntax and length (limit 2048). Raises on error."""
    MAX_LENGTH_URL = 2048
    if len(url) > MAX_LENGTH_URL:
        raise URLTooLong("URL exceeds maximum allowed length", url=url)
    if not validators.url(url):
        raise URLNotValid("URL failed validation", url=url)


def normalize_origin(url: str) -> str:
    """Return origin (scheme://netloc). Drops path, query, fragment."""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def extract_host_key(url: str) -> str:
    """Return netloc (host[:port]) as a compact host key."""
    return urlparse(url).netloc


def get_content(url: str) -> Dict[str, str | int]:
    """Fetch page and extract status_code, h1, title, description."""
    TIME_ANSWER = 10
    response = requests.get(url, timeout=TIME_ANSWER)
    requests.Response.raise_for_status(response)

    soup = BeautifulSoup(response.content, "html.parser")

    status_code = response.status_code
    h1 = soup.find('h1').text if soup.find('h1') else ''
    title = soup.find('title').text if soup.find('title') else ''
    meta_description = soup.find('meta', {'name': "description"})
    description = meta_description["content"] if meta_description else ''

    return {'status_code': status_code,
            'h1': h1,
            'title': title,
            'description': description}
