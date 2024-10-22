import requests
import os.path
from dotenv import load_dotenv
from datetime import datetime

dotenv_path = 'config.env'  # относительный путь до файла с токенами

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

vk_token = os.getenv("VK_TOKEN")
ya_token = os.getenv("YA_TOKEN")


class YandexVKConnector:
    """Класс для инкапсуляции работы с API VK и Яндекса"""
    def __init__(self, token_vk, token_ya):
        self.token_vk = token_vk
        self.token_ya = token_ya
        self.BASE_VK_URL = "https://api.vk.com/method/"
        self.BASE_YA_URL = "https://cloud-api.yandex.net/v1/disk/resources/"

    def get_common_vk_params(self):
        """Метод, возвращающий параметры по умолчанию для работы с API VK"""
        return {
            'access_token': self.token_vk,
            'v': '5.199', 
        }
    
    def get_common_ya_headers(self):
        """Метод, возвращающий параметры по умолчанию для работы с API Яндекс"""
        return {'Authorization': f'OAuth {self.token_ya}'}
        
    def get_photos(self, user_id: int, photo_count=5) -> list[dict]:
        """
        Метод, который возвращает список фотографий
        :user_id: (int) - идентификатор пользователя VK
        :photo_count: (int) - количество скачиваемых фотографий, по умолчанию:5
        """
        params_photos = {
            **self.get_common_vk_params(),
            'owner_id': user_id,
            'album_id': 'profile',
            'count': photo_count,
            'extended': 1,
        }
        url_photos = self.BASE_VK_URL + "photos.get"
        response_photos = requests.get(url_photos, params=params_photos)
        photos = response_photos.json()['response']['items']
        return photos

    def download_upload_photos(self, 
                               user_id: int, 
                               photo_count=5, 
                               folder_name='UsersImages') -> None:
        """
        Метод, который загружает фотографии на компьютер и затем заливает
        их на яндекс диск
        params:
        :user_id: (int) - идентификатор пользователя VK 
        :photo_count: (int) - количество скачиваемых фотографий, по умолчанию:5
        :folder_name: (str) - название папки, которая будет создаваться на ЯД
        """
        self._create_folder(folder_name)  # создание папки 
        photos = self.get_photos(user_id, photo_count)
        for photo in photos:
            likes_count = photo['likes']['count']
            date = str(datetime.fromtimestamp(photo['date'])).split()[0]
            year, month, day = date.split('-')
            for size in photo['sizes']:
                if size['type'] == 'z':
                    response_current_photo = requests.get(size['url'])
                    file_name = f"{likes_count}.png"
                    if os.path.exists(f"users_images/{file_name}"):
                        file_name = file_name[:-4] + f"_{day}-{month}-{year}.png"
                    with open(f"users_images/{file_name}", 'wb') as current_photo:
                        current_photo.write(response_current_photo.content)
                    self._upload_photo(file_name, folder_name)
    
    def _upload_photo(self, name_of_file, folder_name='UsersImages'):
        """Метод, который загружает фотографию на яндекс диск. Не является
        публичным методом"""
        url_upload = self.BASE_YA_URL + "upload"
        params_upload = {
            'path': f'{folder_name}/{name_of_file}',
            'overwrite': True,
        }
        response_upload = requests.get(url_upload, 
                                       params=params_upload,
                                       headers=self.get_common_ya_headers())
        download_link = response_upload.json()['href']

        with open(f"users_images/{name_of_file}", 'rb') as f:
            response = requests.put(download_link, files={'file': f})
            
    def _create_folder(self, folder_name):
        """Метод, создающий папку на яндекс диске. Не является публичным методом"""
        params_create_folder = {
            'path': f'{folder_name}/',
        }
        response = requests.put(self.BASE_YA_URL, 
                                headers=self.get_common_ya_headers(),
                                params=params_create_folder)
    

vlad_bumaga_id = 240651878  # Влад Бумага
connector = YandexVKConnector(vk_token, ya_token)
connector.download_upload_photos(vlad_bumaga_id)