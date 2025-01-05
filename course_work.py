"""Основной модуль программы"""

import os.path
from dotenv import load_dotenv
from social_network_connectors import VKUserConnector, YandexConnector


def read_vk_ya_tokens(path) -> tuple[str]:
    """Функция для чтения токенов."""

    if os.path.exists(path):
        load_dotenv(path)
    else:
        raise FileNotFoundError(
            "Конфигурационный файл не был найден. Перепроверьте маршрут")

    vk_token = os.getenv("VK_TOKEN")
    ya_token = os.getenv("YA_TOKEN")
    return vk_token, ya_token

def main():
    """Основная функция программы"""
    print("Начало работы. Здравствуйте!")
    dotenv_path = 'config.env'  # маршрут конф. файла
    vk_token, ya_token = read_vk_ya_tokens(dotenv_path)  # чтение токенов
    photos_count = 6  # количество фотографий
    username = input("Введите id пользователя ВКонтакте или его псевдоним: ")
    vk_user1 = VKUserConnector(vk_token, username)
    ya_connector = YandexConnector(ya_token)
    ya_connector.download_upload_photos(vk_user1.get_photos(photos_count))
    print("Программа закончила работу. Досвидания")

if __name__ == '__main__':
    main()
