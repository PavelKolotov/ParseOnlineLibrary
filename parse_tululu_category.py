import argparse
import json
import os
import time
from urllib.parse import urljoin

from bs4 import BeautifulSoup

import requests

from main import parse_book_page, download_txt, download_image, check_for_redirect


def get_book_urls(html_content, url):
    book_urls = []
    soup = BeautifulSoup(html_content, 'lxml')
    books_tag = soup.select('table.d_book')
    for book_tag in books_tag:
        book_id = book_tag.select_one('a')['href']
        book_url = urljoin(url, book_id)
        book_urls.append(book_url)
    return book_urls


def main():
    parser = argparse.ArgumentParser(description='Скачивает книги из коллекции фантастических книг '
                                                 'в формате txt с ресурса tululu.org')
    parser.add_argument('-s', '--start_page', help='Начальная страница',
                        default=1, type=int)
    parser.add_argument('-e', '--end_page', help='Конечная страница',
                        default=702, type=int)
    parser.add_argument('-d', '--dest_folder', help='Путь к каталогу',
                        default='books')
    parser.add_argument('-j', '--json_path', help='Путь к json файлу с результатами',
                        default='books')
    parser.add_argument('-s_i', '--skip_img', help='Не скачивать обложки',
                        action="store_true")
    parser.add_argument('-s_t', '--skip_txt', help='Не скачивать книги',
                        action="store_true")
    args = parser.parse_args()
    start_page = args.start_page
    end_page = args.end_page
    folder = args.dest_folder
    json_path = args.json_path
    skip_img = args.skip_img
    skip_txt = args.skip_txt
    book_descriptions = []
    for page in range(start_page, end_page):
        try:
            url = f'https://tululu.org/l55/{page}'
            response = requests.get(url)
            response.raise_for_status()
            check_for_redirect(response)
            book_urls = get_book_urls(response.text, url)
        except requests.HTTPError:
            print(f'Страница отсутствует')
            break
        except requests.ConnectionError:
            print(f'Проблема с интернет-соединением')
            time.sleep(5)
            break
        for book_url in book_urls:
            while True:
                try:
                    response = requests.get(book_url)
                    response.raise_for_status()
                    check_for_redirect(response)
                    book = parse_book_page(response.text, url)
                    book_url = book['book_url']
                    book_name = book['title']
                    img_url = book['img_url']
                    img_name = book['img_name']
                    if not skip_txt:
                        download_txt(book_url, book_name, f'{folder}/{book_name}')
                    if not skip_img:
                        download_image(img_url, img_name, f'{folder}/{book_name}')
                    book_descriptions.append(book)
                    break
                except requests.HTTPError:
                    print(f'Книга {book_name} отсутствует')
                    break
                except requests.ConnectionError:
                    print(f'Проблема с интернет-соединением')
                    time.sleep(5)
    os.makedirs(json_path, exist_ok=True)
    with open(f'{json_path}/book_descriptions.json', 'w') as file:
        json.dump(book_descriptions, file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
