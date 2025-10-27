import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(',')

POSTGRES_DB = os.getenv("POSTGRES_DB", "myprofy_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "myprofy_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "myprofy_pass")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "elasticsearch")
ELASTICSEARCH_PORT = os.getenv("ELASTICSEARCH_PORT", "9200")