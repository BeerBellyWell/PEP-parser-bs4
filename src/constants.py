from pathlib import Path
from enum import Enum


MAIN_DOC_URL = 'https://docs.python.org/3/'
BASE_DIR = Path(__file__).parent
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
PEP_DOC_URL = 'https://peps.python.org/'
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'
# Ищет на странице Python, его версию и статус
LATEST_VERSION_PATTERN = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
# Ищет в теге <а> для скачивания файла в формате zip
DOWNLOAD_PATTERN = r'.+pdf-letter\.zip$'
LXML = 'lxml'
UTF_8 = 'utf-8'


class OutputType(str, Enum):
    PRETTY = 'pretty'
    FILE = 'file'


EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}
