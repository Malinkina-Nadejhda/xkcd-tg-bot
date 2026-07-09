import os
import random
import argparse
import asyncio
from dotenv import load_dotenv
from telegram import Bot, constants
from telegram.error import NetworkError, TimedOut, TelegramError, InvalidToken
from imgs_uploader import download_imgs, create_folder, delete_img
from xkcd import get_latest_comic_num, get_xkcd


async def send_img(bot, tg_chat_id, path):
    with open(path, 'rb') as photo:
        await bot.send_photo(chat_id=tg_chat_id, photo=photo)


async def main():
    load_dotenv()
    parser = argparse.ArgumentParser(
        description=r"""
        Телеграм бот для автоматической публикации комиксов xkcd в чат канала.
        Пример ввода:
        python .\tg_xkcd_bot.py --mode auto # Автоматическая публикация комиксов по заданному интервалу.
        python .\tg_xkcd_bot.py --mode img --path "D:\1.jpg" # Публикация локального изображения.
        """,
        epilog="""
        Для работы бота требуется файл .env с переменной TELEGRAM_TOKEN и TG_CHAT_ID,
        также необходимы файлы imgs_uploader.py и xkcd.py.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter

    )
    parser.add_argument(
        "--mode",
        choices=["img", "auto"],
        default="auto",
        help="img - запостить куртинку,\n"
             "auto - автоматические публикации"
    )
    parser.add_argument(
        "--path",
        type=str,
        help="Путь к папке\n"
             "или изображению"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=int(os.getenv("PUBLIC_INTERVAL", 14400)),
        help="Интервал публикации в секундах\n"
             "По умолчанию 14400 секунд\n"
             "Настраивается в .env файле"
    )
    args = parser.parse_args()
    interval = args.interval
    delay = 10

    try:
        tg_token = os.environ["TELEGRAM_TOKEN"]
        tg_chat_id = os.environ["TG_CHAT_ID"]
    except KeyError:
        print("Ошибка, не найдена переменные 'TELEGRAM_TOKEN' или"
              "'TG_CHAT_ID' в .env файле!")
        return
    try:
        bot = Bot(token=tg_token)
        await bot.get_me()
    except InvalidToken:
        print("Невалидный токен бота, "
              "Проверьте файл .env")
        return
    try:
        await bot.send_chat_action(chat_id=tg_chat_id, action=constants.ChatAction.TYPING)
    except TelegramError:
        print("Отсутсвует id чата, "
              "Проверьте файл .env")
        return
    folder = create_folder("imgs")
    while True:
        try:
            if args.mode == "auto":
                while True:
                    last_comic_num = get_latest_comic_num()
                    comic_num = random.randint(1, last_comic_num)
                    xkcd_info = get_xkcd(comic_num)
                    comic_url = xkcd_info["img"]
                    comment = xkcd_info["alt"]
                    img_path = download_imgs(comic_url, folder)
                    await send_img(bot, tg_chat_id, img_path)
                    await bot.send_message(chat_id=tg_chat_id, text=comment)
                    print("Комикс успешно опубликован.")
                    delete_img(img_path)
                    await asyncio.sleep(interval)
            else:
                if not args.path:
                    print("Для --mode img необходимо указать путь (--path).")
                    await send_img(bot, tg_chat_id, args.path)
                    print("Изображения опубликовано.")
            break
        except (NetworkError, TimedOut):
            print("Ошибка соединения")
            print(f"Повторное соединение через {delay} секунд")
            await asyncio.sleep(delay)
        except FileNotFoundError:
            print("Не найден файл или директория")
            break
        except TypeError:
            print("Неверный тип файла")
            break


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен.")
