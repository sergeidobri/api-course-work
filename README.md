# Курсовая работа на тему "Работа с API"

В ходе работы программа использует ключи доступа (токены) _VK_TOKEN_ и _YA_TOKEN_. Чтобы программа корректно исполнялась, на уровне исполняемого файла `course_work.py` необходимо наличие конфигурационного файла `config.env`, в котором следует прописать соответствующие токены. Пример заполнения представлен в демонстрационном файле `config_example.env`. Программа на вход требует `id` или `screen_name` пользователя и в результате своей работы загружает фотографии с профиля этого пользователя на яндекс диск исполнителя. По умолчанию идет загрузка 5 фото
