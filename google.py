# https://stackoverflow.com/questions/37640297/how-to-retrieve-10-first-google-search-results-using-python-requests

import json
import re

import requests
from bs4 import BeautifulSoup
from requests import Response

headers = {
    'User-agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 '
        'Safari/537.36 Edge/18.19582 '
}


def search(query: str, num_hits: int = 1) -> list:
    """This method searches across google for the specified search text and returns a list of matching documents"""
    html = requests.get(f'https://www.google.com/search?client=ubuntu&channel=fs&q={query}&ie=utf-8&oe=utf-8',
                        headers=headers).text

    soup = BeautifulSoup(html, 'lxml')

    summary = []

    for container in soup.findAll('div', class_='tF2Cxc')[0:num_hits]:
        heading = container.find('h3', class_='LC20lb DKV0Md').text
        article_summary = container.find('span', class_='aCOpRe').text
        link = container.find('a')['href']

        # now visit the article and get the full details
        response: Response = requests.get(url=link)

        if response.status_code != 200:
            print(f'Ign: Failed to get to the {query} article @ {link}')
            continue

        bs = BeautifulSoup(response.text, 'lxml')

        summary.append({
            'keyword': query,
            'heading': heading,
            'summary': article_summary,
            'link': link,
            'text': re.sub("\\s+", ' ', bs.get_text())
        })

        print(f'Scraped for {query} from {link}')

    return summary


