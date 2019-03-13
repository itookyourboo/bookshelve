from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

DATABASE_NAME = "library.db"
TITLE = "bookshelve"
STATUSES = {
    'user': 'Пользователь',
    'moder': 'Модератор',
    'admin': 'Администратор'
}
SORT_BOOKS = [
    ('Book.id.desc()', 'Сначала новые'),
    ('Book.id.asc()', 'Сначала старые'),
    ('Book.title.asc()', 'По названию книги А-Я'),
    ('Book.title.desc()', 'По названию книги Я-А'),
    ('Book.author.asc()', 'По автору А-Я'),
    ('Book.author.desc()', 'По автору Я-А'),
    ('likes asc', 'По лайкам 9-1'),
    ('likes desc', 'По лайкам 1-9'),
    ('comments asc', 'По комментариям 9-1'),
    ('comments desc', 'По комментариям 1-9')
]  # Критерии сортировки для базы данных
SORT_DEFAULT = SORT_BOOKS[6]
MAIN_ADMIN = ('mainadmin', 'admin007')  # Аккаунт главного админа. Нельзя лишить полномочий.

ALLOWED_IMAGES_EXTENSIONS = {'gif', 'jpeg', 'jpg', 'png', 'webp'}
ALLOWED_BOOKS_EXTENSIONS = {'fb2', 'epub', 'mobi', 'pdf', 'kf8', 'djvu' 'rtf', 'txt'}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Макс. размер информации передающийся на сервер (32 Мбайт). При привышении передача будет прервана
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'books')
app.config['BOOKS_COLUMNS'] = 4
db = SQLAlchemy(app)
