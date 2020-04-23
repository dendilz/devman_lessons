import os
import requests
import argparse
from dotenv import load_dotenv

GENERIC_ACCESS_TOKEN = os.getenv('TELEGRAM_TOKEN')

def shorten_link(token, url):
    """
    Возвращает коротую ссылку
    """
    headers = {
        'Authorization': 'Bearer {}'.format(token)
    }
    params = {
        'long_url': '{}'.format(url)
    }

    response = requests.post('https://api-ssl.bitly.com/v4/bitlinks',
                             headers=headers, json=params)
    response.raise_for_status()

    short_url = response.json()['link']

    return short_url

def count_clicks(token, link):
    """
    Возвращает количество кликов по короткой ссылке
    """
    headers = {
        'Authorization': 'Bearer {}'.format(token)
    }

    response = requests.get('https://api-ssl.bitly.com/v4/bitlinks/{}/clicks/summary'.format(link),
                            headers=headers)
    response.raise_for_status()

    return response.json()['total_clicks']


if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser(
        description='Программа обрезает ссылки при помощи Битли'
    )
    parser.add_argument('url', help='Ссылка')
    args = parser.parse_args()

    url = args.url

    try:
        if url.startswith('bit.ly'):
            print('Количество переходов: ', count_clicks(GENERIC_ACCESS_TOKEN, url))
        else:
            print('Битлинк', shorten_link(GENERIC_ACCESS_TOKEN, url))
    except requests.exceptions.HTTPError:
        print('Ошибка 403, проверьте ссылку')
