from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
import os

# from api import *

DATABASE_NAME = "library.db"
TITLE = "bookshelve"
STATUSES = {
    'user': 'Пользователь',
    'moder': 'Модератор',
    'admin': 'Администратор'
}
MAIN_ADMIN = ('mainadmin', 'admin007')

ALLOWED_IMAGES_EXTENSIONS = {'gif', 'jpeg', 'jpg', 'png', 'webp'}
ALLOWED_BOOKS_EXTENSIONS = {'fb2', 'epub', 'mobi', 'pdf', 'kf8', 'djvu' 'rtf', 'txt'}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'books')
app.config['BOOKS_COLUMNS'] = 4
db = SQLAlchemy(app)

# api = Api(app, catch_all_404s=True)
# api.add_resource(BooksListApi, '/', '/api/books')  # для списка объектов
# api.add_resource(BooksApi, '/api/books/<int:book_id>')  # для одного объекта
#
# api.add_resource(UsersListApi, '/api/users')
# api.add_resource(UserApi, '/api/users/<int:user_id>')
