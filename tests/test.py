from requests import get, post, delete, put
from base64 import b64decode, b64encode

print('Регистрация: слишком короткий пароль', post('http://localhost:8000/api/users',
                                                   json={'action': 'register',
                                                         'username': 'new_user',
                                                         'password': '1'}).json())
print('Регистрация: слишком короткий логин', post('http://localhost:8000/api/users',
                                                  json={'action': 'register', 'username': 'user',
                                                        'password': 'password'}).json())
print('Регистрация: недостаточно аргументов', post('http://localhost:8000/api/users',
                                                   json={'action': 'register',
                                                         'username': 'user'}).json())
print('Регистрация: нет аргументов', post('http://localhost:8000/api/users').json())
print('Регистрация: существующий логин', post('http://localhost:8000/api/users',
                                              json={'action': 'register', 'username': 'useruser',
                                                    'password': 'new_password'}).json())
print('Регистрация: успех', post('http://localhost:8000/api/users',
                                 json={'action': 'register', 'username': 'new_user',
                                       'password': 'new_password'}).json())

print('Логин: слишком короткий пароль', post('http://localhost:8000/api/users',
                                             json={'action': 'login', 'username': 'new_user',
                                                   'password': '1'}).json())
print('Логин: слишком короткий логин', post('http://localhost:8000/api/users',
                                            json={'action': 'login', 'username': 'user',
                                                  'password': 'new_password'}).json())
print('Логин: недостаточно аргументов', post('http://localhost:8000/api/users',
                                             json={'action': 'login',
                                                   'username': 'new_user'}).json())
print('Логин: нет аргументов', post('http://localhost:8000/api/users').json())
print('Логин: неправильный логин', post('http://localhost:8000/api/users',
                                        json={'action': 'login', 'username': 'new_user42',
                                              'password': 'new_password'}).json())
print('Логин: неправильный пароль', post('http://localhost:8000/api/users',
                                         json={'action': 'login', 'username': 'new_user',
                                               'password': 'new_password42'}).json())

request_json = post('http://localhost:8000/api/users',
                    json={'action': 'login', 'username': 'new_user',
                          'password': 'new_password'}).json()
print('Логин: успех', request_json)
token = request_json['token']

print('Топ пользователей по количеству загруженных книг:',
      get('http://localhost:8000/api/users', json={'criterion': 'upload'}).json())
print('По поставленным лайкам:',
      get('http://localhost:8000/api/users', json={'criterion': 'liked'}).json())
print('По полученным лайкам:',
      get('http://localhost:8000/api/users', json={'criterion': 'likes'}).json())
print('По оставленным комментариям:',
      get('http://localhost:8000/api/users', json={'criterion': 'commented'}).json())
print('Неправильный критерий топа:',
      get('http://localhost:8000/api/users', json={'criterion': 'wrong criterion'}).json())

print('Информация о пользователе',
      get('http://localhost:8000/api/users/1').json())
print('Информация о несуществующем пользователе',
      get('http://localhost:8000/api/users/1337', json={'criterion': 'wrong criterion'}).json())

print('Изменение статуса пользователя без токена:',
      put('http://localhost:8000/api/users/8', json={'status': 'admin'}).json())
print('Изменение статуса пользователя без доступа:',
      put('http://localhost:8000/api/users/8', json={'token': token, 'status': 'admin'}).json())

print('Бан пользователя без токена:', delete('http://localhost:8000/api/users/8').json())
print('Бан пользователя без доступа:',
      delete('http://localhost:8000/api/users/8', json={'token': token}).json())

request_json = post('http://localhost:8000/api/users',
                    json={'action': 'login', 'username': 'mainadmin',
                          'password': 'admin007'}).json()
token = request_json['token']

print('Изменение статуса пользователя на неправильный:',
      put('http://localhost:8000/api/users/8',
          json={'token': token, 'status': 'wrong status'}).json())
print('Изменение статуса пользователя:', put('http://localhost:8000/api/users/8',
                                             json={'token': token,
                                                   'status': 'Администратор'}).json())
print('Изменение статуса назад:', put('http://localhost:8000/api/users/8',
                                      json={'token': token, 'status': 'Пользователь'}).json())
print('Бан пользователя:',
      delete('http://localhost:8000/api/users/8', json={'token': token}).json())
print('Бан несуществующего пользователя:',
      delete('http://localhost:8000/api/users/138', json={'token': token}).json())
print('Бан пользователя с неправильным индексом:',
      delete('http://localhost:8000/api/users/q', json={'token': token}).json())

print('Получить список книг с неправильной сортировкой:',
      get('http://localhost:8000/api/books', json={'sorting': 'wrong sorting'}).json())
print('Получить список книг с неправильным жанром:', get('http://localhost:8000/api/books',
                                                         json={'sorting': 'Сначала старые',
                                                               'genre_id': 100}).json())

print('Получить список книг по убыванию лайков:',
      get('http://localhost:8000/api/books', json={'sorting': 'По лайкам 9-1'}).json())
print('Получить список книг c определенным жанром по возрастанию id:',
      get('http://localhost:8000/api/books',
          json={'sorting': 'Сначала старые', 'genre_id': 4}).json())

print('Получить информацию о книге без входа:', get('http://localhost:8000/api/books/2').json())
book = get('http://localhost:8000/api/books/2', json={'token': token}).json()
print('Получить информацию о книге:', book)
print('Содержимое книги:', b64decode(book['file']))
print('Получить информацию о несуществующей книге:',
      get('http://localhost:8000/api/books/124212', json={'token': token}).json())

request_json = post('http://localhost:8000/api/users',
                    json={'action': 'login', 'username': 'user1234',
                          'password': 'user1234'}).json()
token_user1 = request_json['token']

request_json = post('http://localhost:8000/api/users',
                    json={'action': 'login', 'username': 'polzovatel',
                          'password': 'polzovatel'}).json()
token_user2 = request_json['token']

print('Залить книгу без входа:', post('http://localhost:8000/api/books',
                                      json={'title': 'Новая книга',
                                            'author': 'Александр Сергеевич Пушкин',
                                            'genre_id': 1,
                                            'description': 'Новая книга великого поэта',
                                            'file': b64encode('Ya Pushkin'.encode()).decode(),
                                            'file_format': 'txt',
                                            'image': book['image'], 'image_format': 'jpg'}).json())

print('Залить книгу без одного из необходимых параметров:',
      post('http://localhost:8000/api/books',
           json={'token': token_user1,
                 'title': 'Новая книга',
                 'author': 'Александр Сергеевич Пушкин',
                 'genre_id': 1,
                 'description': 'Новая книга великого поэта',
                 'file_format': 'txt',
                 'image': book['image'],
                 'image_format': 'jpg'}).json())

print('Залить книгу со слишком длинным параметром:',
      post('http://localhost:8000/api/books',
           json={'token': token_user1,
                 'title': 'Новая книга' * 10,
                 'author': 'Александр Сергеевич Пушкин',
                 'genre_id': 1,
                 'description': 'Новая книга великого поэта',
                 'file': b64encode(
                     'Ya Pushkin'.encode()).decode(),
                 'file_format': 'txt',
                 'image': book['image'],
                 'image_format': 'jpg'}).json())

print('Залить книгу:', post('http://localhost:8000/api/books',
                            json={'token': token_user1, 'title': 'Новая книга',
                                  'author': 'Александр Сергеевич Пушкин',
                                  'genre_id': 1, 'description': 'Новая книга великого поэта',
                                  'file': b64encode('Ya Pushkin'.encode()).decode(),
                                  'file_format': 'txt',
                                  'image': book['image'], 'image_format': 'jpg'}).json())

print('Залилась:', get('http://localhost:8000/api/books/10', json={'token': token_user1}).json())

print('Редактировать книгу без входа:', put('http://localhost:8000/api/books/10',
                                            json={'title': 'Новейшая книга',
                                                  'author': 'А. С. Пушкин',
                                                  'genre_id': 4,
                                                  'description': 'Новая книга величайшего поэта',
                                                  'file': b64encode(
                                                      'Ya Pushkin A. C.'.encode()).decode(),
                                                  'file_format': 'txt',
                                                  'image': book['image'],
                                                  'image_format': 'jpg'}).json())

print('Редактировать книгу другой пользователь:',
      put('http://localhost:8000/api/books/10',
          json={'token': token_user2,
                'title': 'Новейшая книга',
                'author': 'А. С. Пушкин',
                'genre_id': 4,
                'description': 'Новая книга величайшего поэта',
                'file': b64encode(
                    'Ya Pushkin A. C.'.encode()).decode(),
                'file_format': 'txt',
                'image': book['image'],
                'image_format': 'jpg'}).json())

print('Редактировать несуществующую книгу:',
      put('http://localhost:8000/api/books/103212',
          json={'token': token_user1,
                'title': 'Новейшая книга',
                'author': 'А. С. Пушкин',
                'genre_id': 4,
                'description': 'Новая книга величайшего поэта',
                'file': b64encode(
                    'Ya Pushkin A. C.'.encode()).decode(),
                'file_format': 'txt',
                'image': book['image'],
                'image_format': 'jpg'}).json())

print('Редактировать книгу с неправильным индексом:',
      put('http://localhost:8000/api/books/q',
          json={'token': token_user1,
                'title': 'Новейшая книга',
                'author': 'А. С. Пушкин',
                'genre_id': 4,
                'description': 'Новая книга величайшего поэта',
                'file': b64encode(
                    'Ya Pushkin A. C.'.encode()).decode(),
                'file_format': 'txt',
                'image': book['image'],
                'image_format': 'jpg'}).json())

print('Редактировать книгу:', put('http://localhost:8000/api/books/10',
                                  json={'token': token_user1, 'title': 'Новейшая книга',
                                        'author': 'А. С. Пушкин',
                                        'genre_id': 4,
                                        'description': 'Новая книга величайшего поэта',
                                        'file': b64encode(
                                            'Ya Pushkin A. C.'.encode()).decode(),
                                        'file_format': 'txt',
                                        'image': book['image'],
                                        'image_format': 'jpg'}).json())

print('Отредактировалась:',
      get('http://localhost:8000/api/books/10', json={'token': token_user1}).json())

print('Редактировать часть параметров книги:', put('http://localhost:8000/api/books/10',
                                                   json={'token': token_user1,
                                                         'title': 'Сборник стихов Пушкина'}).json())

print('Отредактировалась:',
      get('http://localhost:8000/api/books/10', json={'token': token_user1}).json())

print('Редактировать книгу модератором:',
      put('http://localhost:8000/api/books/10',
          json={'token': token, 'description': 'Новая книга величайшего поэта \
                                              (отредактировано модератором)'}).json())
print('Отредактировалась:',
      get('http://localhost:8000/api/books/10', json={'token': token_user1}).json())

print('Удалить книгу без входа:',
      delete('http://localhost:8000/api/books/10', json={'token': 'assad'}).json())
print('Удалить несуществующую книгу:',
      delete('http://localhost:8000/api/books/100012', json={'token': token_user1}).json())
print('Удалить книгу с неправильным индексом:',
      delete('http://localhost:8000/api/books/q', json={'token': token_user1}).json())
print('Удалить чужую книгу:',
      delete('http://localhost:8000/api/books/2', json={'token': token_user1}).json())
print('Удалить книгу:',
      delete('http://localhost:8000/api/books/10', json={'token': token_user1}).json())
