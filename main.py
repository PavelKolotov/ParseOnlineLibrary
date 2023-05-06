import requests
import os
import re
import argparse


from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError('Книга с данным id отсутствует')


def parse_book_info(html_content, url):
    soup = BeautifulSoup(html_content, 'lxml')
    title_text = soup.find('h1').text
    formated_txt = re.sub(r'\s+', ' ', title_text)
    parts = formated_txt.split(' :: ')
    all_links = soup.find('table', class_='d_book').findAll('a')
    img = soup.find('table', class_='d_book').find('img')['src']
    comments_tags = soup.findAll('div', class_='texts')
    comments = [comment.span.text for comment in comments_tags]
    genres_tags = soup.find('span', class_='d_book').findAll('a')
    genres = [genre.text for genre in genres_tags]
    book_info = {
                'title': parts[0],
                'autor': parts[1],
                'link_txt': urljoin(url, all_links[-3]['href']),
                'img':  urljoin(url, img),
                'img_name': os.path.basename(img),
                'comments': comments,
                'genres': genres
                 }
    return book_info


def download_txt(url, filename, folder='books/'):
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    verified_name = sanitize_filename(filename)
    filepath = os.path.join(folder, f'{verified_name}.txt')
    with open(filepath, 'wb') as file:
        file.write(response.content)
    return filepath


def download_image(url, filename, folder='books/'):
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    verified_name = sanitize_filename(filename)
    filepath = os.path.join(folder, f'{verified_name}')
    with open(filepath, 'wb') as file:
        file.write(response.content)
    return filepath


def main():
    parser = argparse.ArgumentParser(description='Скачиваn книги в формате txt с ресурса tululu.org')
    parser.add_argument('-s', '--start_id', help='Начальный id нкиги', type=int)
    parser.add_argument('-e', '--end_id', help='Начальный id нкиги', type=int)
    args = parser.parse_args()
    start_id = args.start_id
    end_id = args.end_id
    for book_id in range(start_id, end_id + 1):
        url = f'https://tululu.org/b{book_id}/'
        response = requests.get(url)
        response.raise_for_status()
        try:
            check_for_redirect(response)
            book_info = parse_book_info(response.text, url)
            book_url = book_info['link_txt']
            book_name = '.'.join([str(book_id), book_info['title']])
            img_url = book_info['img']
            img_name = book_info['img_name']
            download_txt(book_url, book_name, f'books/{book_name}')
            download_image(img_url, img_name, f'books/{book_name}')

        except requests.HTTPError:
            print(f'Книга по ссылке {url} отсутствует')


if __name__ == "__main__":
    main()