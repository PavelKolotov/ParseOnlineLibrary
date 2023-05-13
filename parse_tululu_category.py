import argparse
import os
import re
import time
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from pathvalidate import sanitize_filename

import requests


def get_books_url(html_content, url):
    books_url = []
    soup = BeautifulSoup(html_content, 'lxml')
    books_tag = soup.findAll('table', class_='d_book')
    for book_tag in books_tag:
        book_id = book_tag.find('a')['href']
        book_url = urljoin(url, book_id)
        books_url.append(book_url)
    return books_url


def main():
    parser = argparse.ArgumentParser(description='Скачивает книги из коллекции фантастических книг '
                                                 'в формате txt с ресурса tululu.org')
    parser.add_argument('-s', '--start_page', help='Начальная страница',
                        default=1, type=int)
    parser.add_argument('-e', '--end_page', help='Конечная страница',
                        default=5, type=int)
    args = parser.parse_args()
    start_page = args.start_page
    end_page = args.end_page
    for page in range(start_page, end_page + 1):
        url = f'https://tululu.org/l55/{page}'
        response = requests.get(url)
        response.raise_for_status()
        get_books_url(response.text, url)


if __name__ == "__main__":
    main()
