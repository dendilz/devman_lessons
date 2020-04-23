import glob
import os
import time
from io import open
from PIL import Image

from instabot import Bot

IMAGES_DIRECTORY = './images/'
POSTED_IMAGES = 'posted.txt'

def get_files_list(path):
    """Получаем список файлов в папке"""
    return os.listdir(path)

def get_coordinates_to_crop(width, height):
    """Получаем координаты, чтобы обрезать картинку"""
    coor = (width - height) // 2
    coor_left = coor
    coor_right = coor + height

    return coor_left, coor_right

def crop_image_for_instagram(images_directory):
    """Обрезаем картинки из папки для инстаграмма"""
    images = get_files_list(images_directory)
    for image in images:
        temp = Image.open(images_directory + '{}'.format(image))

        width, height = temp.width, temp.height
        coor_left, coor_right = get_coordinates_to_crop(width, height)
        coordinates = (coor_left, 0, coor_right, height)

        cropped = temp.crop(coordinates)
        cropped.save(images_directory + '{}'.format(image))

def upload_picture(pic, bot):
    """Загружает фотографию в Instagram"""
    try:
        with open(POSTED_IMAGES, "r", encoding="utf8") as file:
            posted_pic_list = file.read().splitlines()
    except Exception:
        posted_pic_list = []

    if pic not in posted_pic_list:
        print(pic)
        bot.upload_photo(pic)
        if bot.api.last_response.status_code != 200:
            raise ConnectionError

        posted_pic_list.append(pic)
        with open(POSTED_IMAGES, "a", encoding="utf8") as file:
            file.write(pic + "\n")
    time.sleep(60)

def get_images_list():
    """Получаем список изображэений в папке Images"""
    pics = glob.glob(IMAGES_DIRECTORY + "*.*")
    pics = sorted(pics)

    return pics

def main():
    pics = get_images_list()
    crop_image_for_instagram(IMAGES_DIRECTORY)

    bot = Bot()
    bot.login()

    for pic in pics:
        upload_picture(pic, bot)

if __name__ == '__main__':
    main()
