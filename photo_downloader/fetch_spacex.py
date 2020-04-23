import os
import requests

FILENAME_SPACEX = 'spacex{}.jpg'
IMAGES_DIRECTORY = './images/'

def get_images_urls_spacex():
    """Получаем URL картинок из SpaceX"""
    response = requests.get('https://api.spacexdata.com/v3/launches/latest')
    response.raise_for_status()

    urls = response.json()['links']['flickr_images']

    return urls

def fetch_spacex_last_launch():
    """Скачиваем картинки из SpaceX"""
    urls = get_images_urls_spacex()
    for url_number, url in enumerate(urls):
        download_image(FILENAME_SPACEX.format(url_number), url)

def download_image(filename, url):
    """Скачивает картинку с указанного URL и даёт ей имя"""
    response = requests.get(url, verify=False)
    response.raise_for_status()

    with open(IMAGES_DIRECTORY + filename, 'wb') as file:
        file.write(response.content)


if __name__ == '__main__':
    os.makedirs(IMAGES_DIRECTORY, exist_ok=True)

    try:
        fetch_spacex_last_launch()
    except requests.exceptions.HTTPError:
        print('Произошла ошибка, проверьте ссылку')
