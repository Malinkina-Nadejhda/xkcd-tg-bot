import requests


def get_latest_comic_num():
    url = "https://xkcd.com/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    latest_comic_num = response.json()["num"]
    return latest_comic_num


def get_xkcd(comic_num):
    url = f"https://xkcd.com/{comic_num}/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    info = response.json()
    return info
