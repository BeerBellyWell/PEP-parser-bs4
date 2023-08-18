import re
import logging
import requests_cache

from urllib.parse import urljoin
from bs4 import BeautifulSoup
from tqdm import tqdm

from constants import (
    BASE_DIR, MAIN_DOC_URL, PEP_DOC_URL, EXPECTED_STATUS,
    LATEST_VERSION_PATTERN, DOWNLOAD_PATTERN, LXML
)
from configs import configure_argument_parser, configure_logging
from outputs import control_output
from utils import get_response, find_tag


def whats_new(session: 'requests_cache.CachedSession') -> list:
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)

    if response is None:
        return

    soup = BeautifulSoup(response.text, features=LXML)

    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'}
    )

    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = section.find('a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)

        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features=LXML)
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')

        results.append((version_link, h1.text, dl_text))

    return results


def latest_versions(session: 'requests_cache.CachedSession') -> list:
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features=LXML)

    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Ничего не нашлось')

    results = [('Ссылка на документацию', 'Версия', 'Статус')]

    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(LATEST_VERSION_PATTERN, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (link, version, status)
        )

    return results


def download(session: 'requests_cache.CachedSession') -> None:
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features=LXML)

    table_tag = find_tag(soup, 'table', attrs={'class': 'docutils'})

    pdf_letter_tag = find_tag(table_tag, 'a', attrs={
        'href': re.compile(DOWNLOAD_PATTERN)
    })
    pdf_letter_link = pdf_letter_tag['href']
    archive_url = urljoin(downloads_url, pdf_letter_link)

    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename

    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)

    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session: 'requests_cache.CachedSession') -> list:
    response = get_response(session, PEP_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features=LXML)
    section_tag = find_tag(soup, 'section', attrs={'id': 'numerical-index'})
    tbody_tag = find_tag(section_tag, 'tbody')
    tr_tags = tbody_tag.find_all('tr')

    dict_for_result = {
        'Accepted': 0, 'Active': 0, 'Deferred': 0, 'Draft': 0,
        'Final': 0, 'Provisional': 0, 'Rejected': 0, 'Superseded': 0,
        'Withdrawn': 0, 'Total': 0
    }

    for tr in tqdm(tr_tags):
        status_in_table = EXPECTED_STATUS[find_tag(tr, 'abbr').text[1:]]
        pep_link = find_tag(tr, 'a')['href']
        pep_page = urljoin(PEP_DOC_URL, pep_link)
        # Заходим на страницу с конкретным PEP
        response = session.get(pep_page)
        soup = BeautifulSoup(response.text, features=LXML)
        dl_tag = find_tag(soup, 'dl')
        pre_status = dl_tag.find(string='Status')
        status_in_pep_page = pre_status.find_next('dd').text

        if status_in_pep_page not in status_in_table:
            logging.info(
                f'{pep_page}\n'
                f'Статус в карточке: {status_in_pep_page}\n'
                f'Ожидаемые статусы: {status_in_table}\n'
            )
        if status_in_pep_page not in dict_for_result:
            continue
        dict_for_result[status_in_pep_page] += 1
        dict_for_result['Total'] += 1

    results = [('Статус', 'Количество')]
    for k, v in dict_for_result.items():
        results.append((k, v))

    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main() -> None:
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    session = requests_cache.CachedSession()

    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)

    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
