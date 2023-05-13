import argparse
import os
import re
import time
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from pathvalidate import sanitize_filename

import requests


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError('Книга с данным id отсутствует')


def parse_book_page(html_content, url):
    soup = BeautifulSoup(html_content, 'lxml')
    title_text = soup.find('h1').text
    formated_txt = re.sub(r'\s+', ' ', title_text)
    book_title, autor = formated_txt.split(' :: ')
    all_links = soup.find('table', class_='d_book').findAll('a')
    img = soup.find('table', class_='d_book').find('img')['src']
    comments_tags = soup.findAll('div', class_='texts')
    comments = [comment.span.text for comment in comments_tags]
    genres_tags = soup.find('span', class_='d_book').findAll('a')
    genres = [genre.text for genre in genres_tags]
    book = {
        'title': book_title,
        'autor': autor,
        'book_url': urljoin(url, all_links[-3]['href']),
        'img_url':  urljoin(url, img),
        'img_name': os.path.basename(img),
        'comments': comments,
        'genres': genres
    }
    return book


def download_txt(url, filename, folder='books/'):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    os.makedirs(folder, exist_ok=True)
    verified_name = sanitize_filename(filename)
    filepath = os.path.join(folder, f'{verified_name}.txt')
    with open(filepath, 'wb') as file:
        file.write(response.content)



def download_image(url, filename, folder='books/'):
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    verified_name = sanitize_filename(filename)
    filepath = os.path.join(folder, f'{verified_name}')
    with open(filepath, 'wb') as file:
        file.write(response.content)



def main():
    parser = argparse.ArgumentParser(description='Скачивает книги в формате'
                                                 ' txt с ресурса tululu.org')
    parser.add_argument('-s', '--start_id', help='Начальный id нкиги',
                        default=1, type=int)
    parser.add_argument('-e', '--end_id', help='Конечный id нкиги',
                        default=5, type=int)
    args = parser.parse_args()
    start_id = args.start_id
    end_id = args.end_id
    for book_id in range(start_id, end_id + 1):
        url = f'https://tululu.org/b{book_id}/'
        while True:
            try:
                response = requests.get(url)
                response.raise_for_status()
                check_for_redirect(response)
                book = parse_book_page(response.text, url)
                book_url = book['book_url']
                book_name = '.'.join([str(book_id), book['title']])
                img_url = book['img_url']
                img_name = book['img_name']
                download_txt(book_url, book_name, f'books/{book_name}')
                download_image(img_url, img_name, f'books/{book_name}')
                break
            except requests.HTTPError:
                print(f'Книга по ссылке {url} отсутствует')
                break
            except requests.ConnectionError:
                print(f'Проблема с интернет-соединением {url}')
                time.sleep(5)


if __name__ == "__main__":
    main()
