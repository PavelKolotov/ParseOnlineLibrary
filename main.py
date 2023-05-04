import requests
import os


os.makedirs('./books', exist_ok=True)

def download_books(qty):
    for book_id in range(1, qty + 1):
        url = f'https://tululu.org/txt.php?id={book_id}'
        response = requests.get(url)
        response.raise_for_status()
        filename = f'id{book_id}.txt'
        with open(f'./books/{filename}', 'wb') as file:
            file.write(response.content)

download_books(10)
