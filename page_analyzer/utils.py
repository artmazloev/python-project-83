from urllib.parse import urlparse

import requests
import validators
from bs4 import BeautifulSoup


class URLValidationErrors(Exception):
    pass


class URLNotValid(URLValidationErrors):
    pass


class URLTooLong(URLValidationErrors):
    pass


def check_url(url):
    """
    Checks if the provided URL is valid and within the maximum length allowed.

    Parameters:
    url (str): The URL to be checked.

    Raises:
    URLTooLong: If the URL length exceeds the maximum allowed length.
    URLNotValid: If the URL is not a valid URL.

    Returns:
    None
    """
    # Database column length limitation
    MAX_LENGTH_URL = 255
    if len(url) > MAX_LENGTH_URL:
        raise URLTooLong(url)
    if not validators.url(url):
        raise URLNotValid(url)


def normalize_url(url):
    """
    Normalizes the URL by extracting and returning only the scheme and netloc parts.

    Parameters:
    url (str): The URL to be normalized.

    Returns:
    str: The normalized URL containing only the scheme and netloc parts
         (e.g., 'https://www.example.com'). If the original URL lacks a scheme,
         the result may be malformed.

    Example:
        clear_url('https://example.com/path?query=1') returns 'https://example.com'
    """
    parse_url = urlparse(url)
    return f'{parse_url.scheme}://{parse_url.netloc}'


def get_content(url):
    """
    Retrieves specific content elements from the provided URL via HTTP GET request.

    Parameters:
    url (str): The URL from which to extract content.

    Returns:
    dict: A dictionary containing:
        - status_code: HTTP response status code
        - h1: Text content of the first h1 tag (empty string if not found)
        - title: Text content of the title tag (empty string if not found)  
        - description: Content of meta description tag (empty string if not found)

    Raises:
    requests.exceptions.HTTPError: For HTTP error responses
    requests.exceptions.RequestException: For connection/timeout errors
    
    Note:
        Request timeout is set to 10 seconds.
    """
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
