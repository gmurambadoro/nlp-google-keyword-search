# This file performs a Google search for keywords found in the keywords.txt and builds a database for the found
# documents
import datetime
import os
import sys

import requests
from bs4 import BeautifulSoup
from googleScrapy import Google
from pymongo import MongoClient
from requests import Response
from dotenv import load_dotenv

load_dotenv(dotenv_path="./.env")

mongo_url = os.getenv('MONGO_URL')
keyword_filename = os.getenv('KEYWORD_FILE')

client = MongoClient(mongo_url)
database = client.get_database('nlp-keyword-search')
collection = database.get_collection('docs')


class WebPage:
    """Simple representation of a web page to easily extract information out of it as plain text"""

    def __init__(self, soup: BeautifulSoup, url: str):
        self._soup = soup
        self._url = url

    def meta_content(self, meta: str = 'og:title') -> str:
        for _tag in self._soup.find_all('meta'):
            if _tag.get('property', None) == meta:
                return _tag.get('content', '')
        return ''

    def body_text(self) -> str:
        """Extracts the body as plain text"""
        if self._soup.body is None:
            return ""
        body: list = self._soup.body.strings or []
        return " ".join(body)

    def title(self):
        """Extracts the page meta title"""
        return self.meta_content('og:title')

    def description(self):
        """Extracts the page meta description"""
        return self.meta_content('og:description')

    def url(self) -> str:
        return self._url


def google_search(text: str) -> list:
    """Searches Google for the given text and builds a list of pages out of it"""
    pages = []

    search = Google().search(query=text)

    if search['status_code'] != 200:
        print(f'E: Returned response code of {search["status_code"]}')
        sys.exit(1)

    for url in search['links']:
        print(f"Scraping for {text} @ {url} ...")

        # go to this page and scape for information
        response: Response = requests.get(url)

        if response.status_code != 200:
            print(f"Ign: Invalid response code of {response.status_code} returned")
            continue

        bs = BeautifulSoup(response.text, features="html.parser")

        pages.append(WebPage(bs, url))

    return pages


application_list = []
with open(keyword_filename, 'r') as f:
    for line in f.readlines():
        if len(line.strip()) > 3:
            application_list.append(line.strip())

for keyword in application_list:
    search_results = google_search(keyword)

    page: WebPage
    for page in search_results:
        # find this document in the database
        document = dict()
        document['keyword'] = keyword
        document['title'] = page.title()
        document['url'] = page.url()
        document['description'] = page.description()
        document['full_text'] = page.body_text()

        if collection.find_one({"url": page.url(), "keyword": keyword}):
            print(f"Ign: Already searched for {keyword} @ {page.url()}")
            continue

        document['created_at'] = datetime.datetime.now()

        result = collection.insert_one(document)

        if result:
            print(f'OK: Successfully inserted document {keyword} @ {document["url"]}')
        else:
            print(f'E: Failed to insert document {keyword} @ {document["url"]}')