import argparse
import json
import time
from urllib.parse import urljoin

from bs4 import BeautifulSoup

import requests

from main import parse_book_page, download_txt, download_image, check_for_redirect


def get_books_url(html_content, url):
    books_url = []
    soup = BeautifulSoup(html_content, 'lxml')
    books_tag = soup.select('table.d_book')
    for book_tag in books_tag:
        book_id = book_tag.select_one('a')['href']
        book_url = urljoin(url, book_id)
        books_url.append(book_url)
    return books_url


def main():
    parser = argparse.ArgumentParser(description='Скачивает книги из коллекции фантастических книг '
                                                 'в формате txt с ресурса tululu.org')
    parser.add_argument('-s', '--start_page', help='Начальная страница',
                        default=1, type=int)
    parser.add_argument('-e', '--end_page', help='Конечная страница',
                        default=2, type=int)
    args = parser.parse_args()
    start_page = args.start_page
    end_page = args.end_page
    books_description = []
    for page in range(start_page, end_page + 1):
        print(page)
        url = f'https://tululu.org/l55/{page}'
        response = requests.get(url)
        response.raise_for_status()
        books_url = get_books_url(response.text, url)
        for book_url in books_url:
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
                    download_txt(book_url, book_name, f'books/{book_name}')
                    download_image(img_url, img_name, f'books/{book_name}')
                    books_description.append(book)
                    break
                except requests.HTTPError:
                    print(f'Книга {book_name} отсутствует')
                    break
                except requests.ConnectionError:
                    print(f'Проблема с интернет-соединением')
                    time.sleep(5)

    with open("books/books_description.json", "w") as my_file:
        json.dump(books_description, my_file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
