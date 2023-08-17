# Проект парсинга pep

>Парсит информацию о статусе всех существующих PEP.

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
Готово
