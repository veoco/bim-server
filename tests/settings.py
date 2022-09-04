from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

SECRET_KEY = 'fake-key'

INSTALLED_APPS = [
    "tests",
    "speedtests",
]

ROOT_URLCONF = 'tests.urls'
