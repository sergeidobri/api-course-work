"""Классы для работы с API яндекса и Вконтакте"""

from datetime import datetime
import requests
from tqdm import tqdm

class YandexConnector:
    """Класс для инкапсуляции работы с API Яндекса"""
    def __init__(self, token_ya: str):
        self.token_ya = token_ya
        self.base_ya_url = "https://cloud-api.yandex.net/v1/disk/resources/"

    def get_common_ya_headers(self) -> dict:
        """Метод, возвращающий параметры по умолчанию для работы с API Яндекс"""
        return {'Authorization': f'OAuth {self.token_ya}'}

    def download_upload_photos(self,
                               photos: list[dict],
                               folder_name='UsersImages') -> None:
        """
        Метод, который загружает фотографии на компьютер и затем заливает
        их на яндекс диск
        params:
        :photos: (list[dict]) - скачиваемые фотографий, по умолчанию:5
        :folder_name: (str) - название папки, которая будет создаваться на ЯД
        """
        self._create_folder(folder_name)  # создание папки
        print("Начинается загрузка файлов ...")
        for photo in tqdm(photos):
            likes_count = photo['likes']['count']
            date = str(datetime.fromtimestamp(photo['date'])).split()[0]
            year, month, day = date.split('-')
            for size in photo['sizes']:
                if size['type'] == 'z':
                    photo_content = requests.get(size['url'], timeout=10).content
                    file_name = f"{likes_count}_{day}-{month}-{year}.png"
                    self._upload_photo(photo_content, file_name, folder_name)
        print("Загрузка полностью завершена!")

    def _upload_photo(self, photo_bytes, name_of_file, folder_name='UsersImages'):
        """Метод, который загружает фотографию на яндекс диск. Не является
        публичным методом"""
        url_upload = self.base_ya_url + "upload"
        params_upload = {
            'path': f'{folder_name}/{name_of_file}',
            'overwrite': True,
        }
        response_upload = requests.get(url_upload,
                                       params=params_upload,
                                       headers=self.get_common_ya_headers(),
                                       timeout=10)
        download_link = response_upload.json()['href']
        requests.put(
            download_link,
            files={'file': photo_bytes},
            timeout=10)

    def _create_folder(self, folder_name):
        """Метод, создающий папку на яндекс диске. Не является публичным методом"""
        params_create_folder = {
            'path': f'{folder_name}/',
        }
        requests.put(self.base_ya_url,
                    headers=self.get_common_ya_headers(),
                    params=params_create_folder,
                    timeout=10)


class VKUserConnector:
    """Класс для инкапсуляции работы с API VK"""
    def __init__(self, token_vk: str, user_id: str):
        self.token_vk = token_vk
        self.base_vk_url = "https://api.vk.com/method/"

        if not self.is_user_id(user_id):
            user_id = self.get_id_by_screen_name(user_id)

        self.user_id = user_id

    def get_common_vk_params(self) -> dict:
        """Метод, возвращающий параметры по умолчанию для работы с API VK"""
        return {
            'access_token': self.token_vk,
            'v': '5.199', 
        }

    def get_photos(self, photo_count=5) -> list[dict]:
        """
        Метод, который возвращает список фотографий пользователя по его id
        params:
        :photo_count: (int) - количество скачиваемых фотографий, по умолчанию:5
        """
        user_id = self.user_id

        params_photos = {
            **self.get_common_vk_params(),
            'owner_id': user_id,
            'album_id': 'profile',
            'count': photo_count,
            'extended': 1,
        }
        url_photos = self.base_vk_url + "photos.get"
        print("Идёт получение фотографий пользователя ...")
        response_photos = requests.get(url_photos,
                                       params=params_photos,
                                       timeout=10)
        print("Фотографии успешно получены.")
        photos = response_photos.json()['response']['items']
        return photos

    def get_id_by_screen_name(self, user_id: str) -> int:
        """Метод, который получает id пользователя по его screen_name"""
        url_screen_name = self.base_vk_url + 'utils.resolveScreenName'
        params_screen_name = {
            'screen_name': user_id,
            **self.get_common_vk_params(),
        }
        return requests.get(url_screen_name,
                            params=params_screen_name,
                            timeout=10).json()['response']['object_id']

    def get_user_id(self):
        """Метод, который возвращает id пользователя. Метод-геттер"""
        return self.user_id

    @staticmethod
    def is_user_id(user):
        """Утилита для проверки, является ли параметр user id или нет"""
        return all(map(str.isdigit, user))
