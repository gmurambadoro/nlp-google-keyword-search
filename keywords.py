import os

from dotenv import load_dotenv

load_dotenv(dotenv_path="./.env")

keyword_filename = os.getenv('KEYWORD_FILE')

keywords = []
with open(keyword_filename, 'r') as f:
    for line in f.readlines():
        if len(line.strip()) > 3:
            keywords.append(line.strip())

keywords = list(dict.fromkeys(keywords).keys())
