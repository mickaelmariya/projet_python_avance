from pathlib import Path

APP_TITLE = "Projet Python Avancé - Data & Livre"
REPORT_AUTHOR = "Mariyanayagam Mickaël"

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
ASSETS_DIR = BASE_DIR / "assets"
DB_PATH = DATA_DIR / "application.db"

JSON_API_URL = "https://jsonplaceholder.typicode.com/todos"

# Plusieurs adresses officielles Project Gutenberg sont essayées avant le mode secours.
BOOK_TEXT_URLS = (
    "https://www.gutenberg.org/ebooks/11.txt.utf-8",
    "https://www.gutenberg.org/cache/epub/11/pg11.txt",
    "https://dev.gutenberg.org/cache/epub/11/pg11.txt",
)
BOOK_IMAGE_URLS = (
    "https://www.gutenberg.org/cache/epub/11/pg11.cover.medium.jpg",
    "https://dev.gutenberg.org/cache/epub/11/pg11.cover.medium.jpg",
)
BOOK_TEXT_URL = BOOK_TEXT_URLS[0]
BOOK_IMAGE_URL = BOOK_IMAGE_URLS[0]
BOOK_SOURCE_URL = "https://www.gutenberg.org/ebooks/11"

BACKUP_BOOK_TEXT_PATH = ASSETS_DIR / "alice_backup.txt"
BACKUP_BOOK_IMAGE_PATH = ASSETS_DIR / "alice_cover_backup.jpg"
BOOK_TEXT_CACHE_PATH = DATA_DIR / "alice_book_cache.txt"
BOOK_IMAGE_CACHE_PATH = DATA_DIR / "alice_cover_cache.jpg"

# Timeout séparé connexion/lecture. Le programme passe ensuite automatiquement
# à une copie locale de secours pour ne jamais bloquer la démonstration.
NETWORK_TIMEOUT = (5, 10)
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 ProjetPythonAvance/2.0"
)
