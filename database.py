import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv(dotenv_path="./.env")

mongo_url = os.getenv('MONGO_URL')

client = MongoClient(mongo_url)
database = client.get_database('nlp-keyword-search')
collection = database.get_collection('docs')
