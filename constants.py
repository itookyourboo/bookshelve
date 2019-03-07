from flask import Flask
from flask_sqlalchemy import SQLAlchemy


DATABASE_NAME = "library.db"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)