

import os
import logging
import sys
from download import download


LITECODER_ENV = os.environ.get('LITECODER_ENV')

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

US_STATE_PATH = os.path.join(DATA_DIR, 'us-states.marisa')

US_CITY_PATH = os.path.join(DATA_DIR, 'us-cities.marisa')

LITECODER_DB_PATH = os.path.join(DATA_DIR, 'litecoder.db')

CITY_ALT_NAMES_PATH = os.path.join(DATA_DIR, 'city-alt-names.yml')

CITY_ALT_NAMES_URL = "https://github.com/Sheshank-s/litecoder/releases/download/v1.0/city-alt-names.yml"

LITECODER_DB_URL = "https://github.com/Sheshank-s/litecoder/releases/download/v1.0/litecoder.db"

if not os.path.isfile(CITY_ALT_NAMES_PATH):
    download(CITY_ALT_NAMES_URL, CITY_ALT_NAMES_PATH, progressbar=True, verbose=False)

if not os.path.isfile(LITECODER_DB_PATH):
    download(LITECODER_DB_URL, LITECODER_DB_PATH, progressbar=True, verbose=False)

logging.basicConfig(
    format='%(asctime)s | %(levelname)s : %(message)s',
    stream=sys.stdout,
    level=logging.INFO,
)

logger = logging.getLogger('litecoder')
