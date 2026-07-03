import urllib.parse
import os.path
import requests


def create_folder(folder):
    absolute_path = os.path.abspath(folder)
    os.makedirs(absolute_path, exist_ok=True)
    return absolute_path


def download_imgs(img_url, absolute_path, params=None):
    response = requests.get(img_url, params=params)
    response.raise_for_status()
    parsed_img_url = urllib.parse.urlparse(img_url)
    img_name = os.path.basename(parsed_img_url.path)
    image_path = os.path.join(absolute_path, img_name)
    with open(image_path, "wb") as file:
        file.write(response.content)
    return image_path


def delete_img(img_path):
    if os.path.exists:
        os.remove(img_path)
    else:
        print("Файл не найден.")
