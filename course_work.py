import requests
import os.path
from dotenv import load_dotenv
from datetime import datetime
from tqdm import tqdm


class YandexConnector:
    """Класс для инкапсуляции работы с API Яндекса"""
    def __init__(self, token_ya: str):
        self.token_ya = token_ya
        self.BASE_YA_URL = "https://cloud-api.yandex.net/v1/disk/resources/"

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
                    photo_content = requests.get(size['url']).content
                    file_name = f"{likes_count}_{day}-{month}-{year}.png"
                    self._upload_photo(photo_content, file_name, folder_name)
        print("Загрузка полностью завершена!")
    
    def _upload_photo(self, photo_bytes, name_of_file, folder_name='UsersImages'):
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
        response_upload_photo = requests.put(download_link, files={'file': photo_bytes})
            
    def _create_folder(self, folder_name):
        """Метод, создающий папку на яндекс диске. Не является публичным методом"""
        params_create_folder = {
            'path': f'{folder_name}/',
        }
        response_create_folder = requests.put(self.BASE_YA_URL, 
                                headers=self.get_common_ya_headers(),
                                params=params_create_folder)
    

class VKUserConnector:
    """Класс для инкапсуляции работы с API VK"""
    def __init__(self, token_vk: str, user_id: str):
        self.token_vk = token_vk
        self.BASE_VK_URL = "https://api.vk.com/method/"
        
        is_user_id = lambda x: all(map(str.isdigit, x))
        if not is_user_id(user_id): user_id = self.get_id_by_screen_name(user_id)

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
        url_photos = self.BASE_VK_URL + "photos.get"
        print("Идёт получение фотографий пользователя ...")
        response_photos = requests.get(url_photos, params=params_photos)
        print("Фотографии успешно получены.")
        photos = response_photos.json()['response']['items']
        return photos
    
    def get_id_by_screen_name(self, user_id: str) -> int:
        """Метод, который получает id пользователя по его screen_name"""
        url_screen_name = self.BASE_VK_URL + 'utils.resolveScreenName'
        params_screen_name = {
            'screen_name': user_id,
            **self.get_common_vk_params(),
        }
        return requests.get(url_screen_name, 
                            params=params_screen_name).json()['response']['object_id']
    
    def get_user_id(self):
        """Метод, который возвращает id пользователя. Метод-геттер"""
        return self.user_id


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
