import os
from constants import *
from base64 import b64decode

from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired
from flask import Flask
from flask import request, redirect, url_for, render_template, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_restful import reqparse, abort, Api, Resource
from requests import get, post, delete, put


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Модель пользователя
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(160), nullable=False)
    status = db.Column(db.String(80))

    def __repr__(self):
        return f'User ID{self.id}. {self.username}: {self.status}'


# Модель книги
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    # author = db.relationship('Author', backref=db.backref('books', lazy=True))
    # genre = db.relationship('Genre', backref=db.backref('books', lazy=True))
    description = db.Column(db.String(1000), nullable=False)

    uploader_id = db.Column(db.Integer,
                            db.ForeignKey('user.id'),
                            nullable=False)
    uploader = db.relationship('User', backref=db.backref('books', lazy=True))
    image = db.Column(db.String(200))
    file = db.Column(db.String(200))

    def __repr__(self):
        return f'{self.name}, {self.author.name}'


# Модель автора
class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    image = db.Column(db.String(80))
    description = db.Column(db.String(1000))


# Модель жанра
class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))


# Модель лайка
class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)


db.create_all()


class BooksApi(Resource):
    put_parser = reqparse.RequestParser()
    put_parser.add_argument('title')
    put_parser.add_argument('description')
    put_parser.add_argument('file')
    put_parser.add_argument('format')

    def get(self, book_id):  # Получить информацию о книге
        book = abort_if_book_not_found(book_id)
        return jsonify({'title': book.title, 'description': book.description, 'file': book})

    def delete(self, book_id):  # Удалить книгу
        abort_if_book_not_found(book_id)
        Book.query.filter_by(id=book_id).delete()
        db.session.commit()
        return jsonify({'success': 'OK'})

    def put(self, book_id):  # Редактировать информацию о книге
        book = abort_if_book_not_found(book_id)
        args = BooksApi.put_parser.parse_args()
        if all(val is None for key, val in args.items()):
            abort(400, message="{}: 'Missing required parameter in the JSON body or the post "
                               "body or the query string'".format(' | '.join(args.keys())))

        if args['file']:
            with open(book.file, 'wb') as f:
                f.write(b64decode(args['file']))
            args.pop('file')
        if args['title'] or args['format']:
            filename = "_".join((args['title'] if args['title'] else book.title).split())
            extension = args['format'] if args['format'] else os.path.splitext(book.file)[1]

            cwd = os.getcwd()
            os.chdir(cwd + '/static/books')
            os.rename(book.file[book.file.rfind('/')+1:], f'{filename}{extension}')
            book.file = '/static/books/' + filename + extension
            os.chdir(cwd)
            args.pop('format', 0)


        Book.query.filter_by(id=book_id).update(args)
        db.session.commit()
        return jsonify({'success': 'OK'})


class BooksListApi(Resource):
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('title', required=True)
    post_parser.add_argument('description', required=True)
    post_parser.add_argument('file', required=True)
    post_parser.add_argument('format', required=True)

    def get(self):  # В будущем тут можно возвращать недавно добавленные книги
        books = Book.query.all()
        return jsonify({'books': [[book.title] for book in books]})

    def post(self):  # Добавить книгу
        args = BooksListApi.post_parser.parse_args()
        path = f'static/books/{"_".join(args["title"].split())}.{args["format"]}'

        book = Book(title=args['title'], description=args['description'], file=path)
        user = User.query.filter_by(id=session['user_id']).first()
        user.books.append(book)
        with open(path, 'wb') as f:
            f.write(b64decode(args['file']))
        db.session.commit()
        return jsonify({'success': 'OK'})


class UserApi(Resource):
    put_parser = reqparse.RequestParser()
    put_parser.add_argument('password', required=True)

    def get(self, user_id):  # Информация о пользователе. Потом можно будет возвращать загруженные, понравившиеся книги.
        user = abort_if_user_not_found(user_id)
        return jsonify({'user': [user.username, user.status, user.books]})

    def delete(self, user_id):  # Удалить пользователя
        abort_if_user_not_found(user_id)
        User.query.filter_by(id=user_id).delete()
        db.session.commit()
        return jsonify({'success': 'OK'})

    def put(self, user_id):  # Изменить пароль
        abort_if_user_not_found(user_id)
        args = UserApi.put_parser.parse_args()
        User.query.filter_by(id=user_id).update(
            {'password_hash': generate_password_hash(args['password'])})
        db.session.commit()
        return jsonify({'success': 'OK'})


class UsersListApi(Resource):
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('action', required=True)
    post_parser.add_argument('username', required=True)
    post_parser.add_argument('password', required=True)

    def get(self):
        users = User.query.all()
        return jsonify({'users': [[user.id, user.username, len(user.books)] for user in users]})

    def post(self):  # Логин/регистрация
        args = UsersListApi.post_parser.parse_args()
        if args['action'] == 'register':
            if User.query.filter_by(username=args['username']).first() is not None:
                return jsonify({'error': 'user "{}" already exists'.format(args['username'])})
            user = User(username=args['username'],
                                 password_hash=generate_password_hash(args['password']))
            db.session.add(user)
            db.session.commit()
        elif args['action'] == 'login':
            user = User.query.filter_by(username=args['username']).first()
            if user is None or not check_password_hash(user.password_hash, args['password']):
                return jsonify({'error': 'wrong login or password'})
        else:
            abort(404, message="wrong action {}".format(args['action']))
        session['user_id'] = user.id
        session['username'] = user.username
        print(session)
        return jsonify({'success': 'OK'})


def abort_if_book_not_found(book_id):
    book = Book.query.filter_by(id=book_id).first()
    if book:
        return book
    abort(404, message="Book {} not found".format(book_id))


def abort_if_user_not_found(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user:
        return user
    abort(404, message="User {} not found".format(user_id))


api = Api(app, catch_all_404s=True)
api.add_resource(BooksListApi, '/', '/api/books')  # для списка объектов
api.add_resource(BooksApi, '/api/books/<int:book_id>')  # для одного объекта

api.add_resource(UsersListApi, '/api/users')
api.add_resource(UserApi, '/api/users/<int:user_id>')


# Вход в систему
def login_user(username, password):
    userModel = User.query.filter_by(username=username).first()
    if userModel and check_password_hash(userModel.password_hash, password):
        return True, {
            'username': username,
            'user_id': userModel.id
        }
    return False, 'Неверный логин или пароль'


# Регистрация
def logup_user(username, password):
    userModel = User.query.filter_by(username=username).first()
    if userModel:
        return False, 'Пользователь с таким логином уже существует'
    else:
        user = User(username=username,
                    password_hash=generate_password_hash(password),
                    status=STATUSES['user'])
        db.session.add(user)
        db.session.commit()
        return True, {
            'username': username,
            'user_id': user.id
        }


# Выход из системы
def logout_user(session):
    session.pop('username', 0)
    session.pop('user_id', 0)


# Изменить статус пользователя (пользователь, модератор, администратор)
def change_status(user_id, status):
    user = User.query.filter_by(id=user_id).first()
    user.status = status
    db.session.commit()


# Поставить лайк / убрать лайк
def like(user_id, book_id):
    like = Like.query.filter_by(user_id=user_id, book_id=book_id).first()
    if like:
        db.session.delete(like)
    else:
        db.session.add(Like(user_id=user_id, book_id=book_id))
    db.session.commit()


# Количество лайков у книги
def get_likes(book_id):
    return Like.query.filter_by(book_id=book_id).count()


# Добавление жанра
def add_genre(name):
    db.session.add(Genre(name=name))
    db.session.commit()


# Изменение названия жанра
def edit_genre(old_name, new_name):
    genre = Genre.query.filter_by(name=old_name).first()
    genre.name = new_name
    db.session.commit()


# Удаление жанра
def delete_genre(name):
    genre = Genre.query.filter_by(name=name).first()
    db.session.delete(genre)
    db.session.commit()


# Редактирование автора
def edit_author(id, **keys):
    author = Author.query.filter_by(id=id).first()
    for key in keys:
        exec(f'author.{key} = {keys[key]}')
    db.session.commit()


# Редактирование книги
def edit_book(id, **keys):
    book = Book.query.filter_by(id=id).first()
    for key in keys:
        exec(f'book.{key} = {keys[key]}')
    db.session.commit()


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    login = SubmitField('Войти')
    logup = SubmitField('Регистрация')


class LogupForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    logup = SubmitField('Регистрация')


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    if 'username' not in session:
        return redirect('/login')

    return render_template('index.html', title=TITLE, session=session)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        is_login_form = form.login.data
        if is_login_form:
            username = form.username.data
            password = form.password.data
            result = login_user(username, password)
            if result[0]:
                session['username'], session['user_id'] = result[1]['username'], result[1]['user_id']
                return redirect('/index')
            return render_template('login.html', error=result[1], title=TITLE, form=form)
        return redirect('/logup')
    return render_template('login.html', title=TITLE, form=form)


@app.route('/logup', methods=['GET', 'POST'])
def logup():
    form = LogupForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        result = logup_user(username, password)
        if result[0]:
            session['username'], session['user_id'] = result[1]['username'], result[1]['user_id']
            return redirect('/index')
        return render_template('logup.html', error=result[1], title=TITLE, form=form)
    return render_template('logup.html', title=TITLE, form=form)


@app.route('/logout')
def logout():
    logout_user(session)
    return redirect('/index')


if __name__ == '__main__':
    app.run(port=8000, host='127.0.0.1')