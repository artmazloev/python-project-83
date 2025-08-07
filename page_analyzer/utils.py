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
    MAX_LENGTH_URL = 255
    if len(url) > MAX_LENGTH_URL:
        raise URLTooLong()
    if not validators.url(url):
        raise URLNotValid()


def clear_url(url):
    """
    Clears the URL by extracting and returning the scheme and netloc parts.

    Parameters:
    url (str): The URL to be cleared.

    Returns:
    str: The cleared URL containing only the scheme
    and netloc parts(https://www.example.com).
    """
    parse_url = urlparse(url)
    return f'{parse_url.scheme}://{parse_url.netloc}'


def get_content(url):
    """
    Retrieves specific content elements from the provided URL
    and returns a dictionary with the results.

    Parameters:
    url (str): The URL from which to extract content.

    Returns:
    dict: A dictionary containing the status code, h1 tag text,
    title text, and description content.
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
