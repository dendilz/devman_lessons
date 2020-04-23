import os
import requests
from random import randint
from dotenv import load_dotenv


def get_number_of_last_comics():
    """Получаем номер полседнего комикса на xkcd"""
    response = requests.get('http://xkcd.com/info.0.json')
    response.raise_for_status()

    data = response.json()
    number = data['num']

    return number


def get_comics_url_xkcd(number):
    """Получаем URL и комментарий комикса из xkcd"""
    response = requests.get('https://xkcd.com/{}/info.0.json'.format(number))
    response.raise_for_status()

    data = response.json()
    url = data['img']
    comment = data['alt']

    return url, comment


def download_image(url, filename):
    """Скачиваем картинку по URL"""
    response = requests.get(url)
    response.raise_for_status()

    with open(filename, 'wb') as file:
        file.write(response.content)


def get_wall_upload_server(access_token):
    """Получить ссылку, на которую отправим картинку"""
    params = {
        'access_token': access_token,
        'v': '5.103'
    }
    response = requests.get('https://api.vk.com/method/photos.getWallUploadServer', params=params)
    response.raise_for_status()

    if 'error' in response:
        raise requests.exceptions.HTTPError(response['error']['error_msg'])

    data = response.json()['response']
    upload_url = data['upload_url']

    return upload_url


def upload_image(filename, url):
    """Отправляем картинку"""
    with open(filename, 'rb') as file:
        files = {
            'photo': file,
        }
        response = requests.post(url, files=files)
        response.raise_for_status()

        if 'error' in response:
            raise requests.exceptions.HTTPError(response['error']['error_msg'])

        data = response.json()
        server = data['server']
        photo = data['photo']
        hash_vk = data['hash']

        return server, photo, hash_vk


def save_image(access_token, server, photo, hash_vk):
    """Сохраняем картинку после отправки"""
    params = {
        'access_token': access_token,
        'server': server,
        'photo': photo,
        'hash': hash_vk,
        'v': '5.103'
    }
    response = requests.post('https://api.vk.com/method/photos.saveWallPhoto',
                             params=params)
    response.raise_for_status()

    if 'error' in response:
        raise requests.exceptions.HTTPError(response['error']['error_msg'])

    data = response.json()['response'][0]
    media_id = data['id']
    owner_id = data['owner_id']

    return media_id, owner_id


def public_image(access_token, message, id, group_id, owner_id, from_group=0):
    """Публикуем картинку на стену"""
    params = {
        'access_token': access_token,
        'owner_id': -group_id,
        'from_group': from_group,
        'message': message,
        'attachments': 'photo{}_{}'.format(owner_id, id),
        'v': '5.103'
    }
    response = requests.post('https://api.vk.com/method/wall.post',
                             params=params)
    response.raise_for_status()

    if 'error' in response:
        raise requests.exceptions.HTTPError(response['error']['error_msg'])


def delete_image(filename):
    """Удаляем опубликованную картинку"""
    os.remove(filename)


def main():
    load_dotenv()
    filename = 'comics.png'
    comics_number = randint(1, get_number_of_last_comics())

    access_token = os.getenv('VK_ACCESS_TOKEN')
    album_id = os.getenv('VK_ALBUM_ID')
    try:
        url, comment = get_comics_url_xkcd(comics_number)
        download_image(url, filename)

        upload_url = get_wall_upload_server(access_token)
        server, photo, hash_vk = upload_image(filename, upload_url)
        media_id, owner_id = save_image(access_token, server, photo, hash_vk)
        public_image(access_token, comment, media_id, int(album_id), owner_id)

    except requests.HTTPError:
        print('Ошибка, проверьте правильность запроса')
    except PermissionError:
        print('Ошибка удаления файла, проверьте, что он не используется')
    finally:
        delete_image(filename)


if __name__ == '__main__':
    main()
