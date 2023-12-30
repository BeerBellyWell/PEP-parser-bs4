# Проект парсинга pep

>Парсит информацию о статусе всех существующих PEP, ссылки на документацию, версии и статусы Python, ссылки на документацию актуальной версии Python.

Стек: Python v3.9, BeautifulSoup4, Git.
#### Как запустить проект:

+ клонируем репозиторий `git clone`
`https://github.com/BeerBellyWell/bs4_parser_pep`
+ переходим в него `cd bs4_parser_pep`
    + разворачиваем виртуальное окружение
    `python3 -m venv env` (Windows: `python -m venv env`)
    + активируем его
    `source env/bin/activate` (Windows: `source env/scripts/activate`)
    + устанавливаем зависимости из файла requirements.txt
    `pip install -r requirements.txt`
+ запускаем парсер
`cd src` переходим в директорию с файлом main.py
`python main.py pep -o file`

#### Работа с проектом:
Вызвать команду `python main.py -h` для справки:
```
usage: main.py [-h] [-c] [-o {OutputType.PRETTY,OutputType.FILE}]
               {whats-new,latest-versions,download,pep}

Парсер документации Python

positional arguments:
  {whats-new,latest-versions,download,pep}
                        Режимы работы парсера

optional arguments:
  -h, --help            show this help message and exit
  -c, --clear-cache     Очистка кеша
  -o {OutputType.PRETTY,OutputType.FILE}, --output {OutputType.PRETTY,OutputType.FILE}
                        Дополнительные способы вывода данных
```
