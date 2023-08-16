import re
import logging
import requests_cache

from urllib.parse import urljoin
from bs4 import BeautifulSoup
from tqdm import tqdm

from constants import BASE_DIR, MAIN_DOC_URL, PEP_DOC_URL, EXPECTED_STATUS
from configs import configure_argument_parser, configure_logging
from outputs import control_output
from utils import get_response, find_tag


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)

    if response is None:
        # Если основная страница не загрузится, программа закончит работу.
        return

    soup = BeautifulSoup(response.text, features='lxml')

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
            # Если страница не загрузится,
            # программа перейдёт к следующей ссылке.
            continue
        soup = BeautifulSoup(response.text, features='lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')

        results.append((version_link, h1.text, dl_text))

    return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')

    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')

    # Перебор в цикле всех найденных списков.
    for ul in ul_tags:
        # Проверка, есть ли искомый текст в содержимом тега.
        if 'All versions' in ul.text:
            # Если текст найден, ищутся все теги <a> в этом списке.
            a_tags = ul.find_all('a')
            # Остановка перебора списков.
            break
    # Если нужный список не нашёлся,
    # вызывается исключение и выполнение программы прерывается.
    else:
        raise Exception('Ничего не нашлось')
    # print(a_tags)

    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'

    for a_tag in a_tags:
        # Извлечение ссылки.
        link = a_tag['href']
        # Поиск паттерна в ссылке.
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            # Если строка соответствует паттерну,
            # переменным присываивается содержимое групп, начиная с первой.
            version, status = text_match.groups()
        else:
            # Если строка не соответствует паттерну,
            # первой переменной присваивается весь текст, второй—пустая строка
            version, status = a_tag.text, ''
        # Добавление полученных переменных в список в виде кортежа.
        results.append(
            (link, version, status)
        )

    # Печать результата.
    return results


def download(session):
    # Вместо константы DOWNLOADS_URL, используйте переменную downloads_url.
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')

    table_tag = find_tag(soup, 'table', attrs={'class': 'docutils'})

    pdf_letter_tag = find_tag(table_tag, 'a', attrs={
        'href': re.compile(r'.+pdf-letter\.zip$')
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


def pep(session):
    response = get_response(session, PEP_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
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
        soup = BeautifulSoup(response.text, features='lxml')
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
            # dict_for_result['Total'] += 1 # Нужно ли плюсовать в ТОТАЛ?
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


def main():
    # Запускаем функцию с конфигурацией логов.
    configure_logging()
    # Отмечаем в логах момент запуска программы.
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    # Парсит аргументы командной строки
    args = arg_parser.parse_args()

    # Логируем переданные аргументы командной строки.
    logging.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession()

    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)

    # Если из функции вернулись какие-то результаты,
    if results is not None:
        # передаём их в функцию вывода вместе с аргументами командной строки.
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
