from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from api import *

DATABASE_NAME = "library.db"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app, catch_all_404s=True)
api.add_resource(BooksListApi, '/', '/api/books')  # для списка объектов
api.add_resource(BooksApi, '/api/books/<int:book_id>')  # для одного объекта

api.add_resource(UsersListApi, '/api/users')
api.add_resource(UserApi, '/api/users/<int:user_id>')
