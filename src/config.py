from dotenv import load_dotenv
import os


load_dotenv()

API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')
TG_USERNAME = os.environ.get('TG_USERNAME')

DB_HOST = os.environ.get('DB_HOST')
DB_NAME = os.environ.get('DB_NAME')
DB_PASS = os.environ.get('DB_PASS')
DB_PORT = os.environ.get('DB_PORT')
DB_USER = os.environ.get('DB_USER')
