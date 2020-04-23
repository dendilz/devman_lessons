import os
import requests
import argparse

FILENAME_HUBBLE = 'hubble{}.{}'
IMAGES_DIRECTORY = './images/'

def get_images_urls_hubble(image_id):
    """Получаем URL картинок из Hubble по ID"""
    response = requests.get('http://hubblesite.org/api/v3/image/{}'.format(image_id))
    response.raise_for_status()
    urls = []
    data = response.json()['image_files']
    for subject in data:
        urls.append('https:' + subject['file_url'])

    return urls

def fetch_images_from_hubble(collection_name):
    """Скачиваем картинки из коллекции Hubble"""
    ids = get_id_from_collection_hubble(collection_name)
    for image_id in ids:
        fetch_image_from_hubble(image_id)

def get_extension_from_url(url):
    """Возвращает расширение файла из URL"""
    extension = os.path.splitext(url)[1].replace('.', '')
    return extension

def fetch_image_from_hubble(image_id):
    """Скачиваем картинку по ID из Hubble"""
    urls = get_images_urls_hubble(image_id)
    url = urls[-1]
    extension = get_extension_from_url(url)
    download_image(FILENAME_HUBBLE.format(image_id, extension), url)

def get_id_from_collection_hubble(collection_name):
    """Получаем ID фотографий из коллекции"""
    response = requests.get('http://hubblesite.org/api/v3/images/{}'.format(collection_name))
    response.raise_for_status()
    data = response.json()
    ids = []
    for subject in data:
        ids.append(subject['id'])

    return ids

def download_image(filename, url):
    """Скачивает картинку с указанного URL и даёт ей имя"""
    response = requests.get(url, verify=False)
    response.raise_for_status()

    with open(IMAGES_DIRECTORY + filename, 'wb') as file:
        file.write(response.content)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Программа скачивает фотографии из коллекции Hubble'
    )
    parser.add_argument('collection_name', help='Название коллекции, например '
                                                '"holiday_cards", "wallpaper", "spacecraft", '
                                                '"news", "printshop", "stsci_gallery"')

    args = parser.parse_args()
    collection_name = args.collection_name

    os.makedirs(IMAGES_DIRECTORY, exist_ok=True)

    try:
        fetch_images_from_hubble(collection_name)
    except requests.exceptions.HTTPError:
        print('Произошла ошибка, проверьте ссылку')
