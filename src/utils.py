import logging

from requests import RequestException
from exceptions import ParserFindTagException
from requests_cache import CachedSession
from bs4 import BeautifulSoup
from requests_cache.models.response import CachedResponse
from bs4.element import Tag
from constants import UTF_8


def get_response(session: 'CachedSession', url: str) -> 'CachedResponse':
    '''Перехват ошибки RequestException.'''
    try:
        response = session.get(url)
        response.encoding = UTF_8
        return response

    except RequestException:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {url}',
            stack_info=True
        )


def find_tag(soup: 'BeautifulSoup', tag: str, attrs: dict = None) -> 'Tag':
    '''Перехват ошибкт поиска тегов'''
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag
