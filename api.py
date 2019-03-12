from flask import jsonify, session
from flask_restful import reqparse, abort, Api, Resource
import dbhelper
from werkzeug.security import generate_password_hash, check_password_hash
from base64 import b64decode, b64encode
from constants import app, SORT_BOOKS, ALLOWED_IMAGES_EXTENSIONS, ALLOWED_BOOKS_EXTENSIONS
import os
import string
import random
import functions

TOKEN_CHARSET = list(string.ascii_lowercase + string.ascii_uppercase + string.digits)
tokens_ids, ids_tokens = {}, {}


def generate_token(user_id):
    token = ''.join(random.choice(TOKEN_CHARSET) for i in range(16))
    while token in tokens_ids:
        token = ''.join(random.choice(TOKEN_CHARSET) for i in range(16))
    if user_id in ids_tokens:
        del tokens_ids[ids_tokens[user_id]]
    tokens_ids[token] = user_id
    ids_tokens[user_id] = token
    return token


class BooksApi(Resource):
    delete_parser = reqparse.RequestParser()
    delete_parser.add_argument('token', required=True)

    get_parser = reqparse.RequestParser()
    get_parser.add_argument('token')

    put_parser = reqparse.RequestParser()
    put_parser.add_argument('token', required=True)
    put_parser.add_argument('title')
    put_parser.add_argument('author')
    put_parser.add_argument('description')
    put_parser.add_argument('genre_id', type=int)
    put_parser.add_argument('file')
    put_parser.add_argument('file_format')
    put_parser.add_argument('image')
    put_parser.add_argument('image_format')

    def get(self, book_id):  # Получить информацию о книге
        args = BooksApi.get_parser.parse_args()
        book = abort_if_book_not_found(book_id)
        json = {'id': book.id, 'title': book.title, 'author': book.author,
                'genre_id': book.genre_id,
                'description': book.description, 'uploader_id': book.uploader_id,
                'image': book.image,
                'likes': book.likes, 'comments': book.comments}
        if book.image:
            with open(book.image, 'rb') as f:
                json['image'] = b64encode(f.read()).decode()
                json['image_format'] = book.image.rsplit('.')[1]
        if args['token'] is not None and args['token'] in tokens_ids:
            with open(book.file, 'rb') as f:
                json['file'] = b64encode(f.read()).decode()
                json['file_format'] = book.file.rsplit('.')[1]

        return jsonify(json)

    def delete(self, book_id):  # Удалить книгу
        args = BooksApi.delete_parser.parse_args()
        book = abort_if_book_not_found(book_id)
        if book.uploader_id != tokens_ids.get(args['token']) and dbhelper.Moder.query.filter_by(
                user_id=tokens_ids.get(args['token'])).first() is None:
            return jsonify({'error': 'access denied'})
        functions.delete_book(book_id)
        return jsonify({'success': 'OK'})

    def put(self, book_id):  # Редактировать информацию о книге
        book = abort_if_book_not_found(book_id)
        args = BooksApi.put_parser.parse_args()

        if book.uploader_id != tokens_ids.get(args['token']) and dbhelper.Moder.query.filter_by(
                user_id=tokens_ids.get(args['token'])).first() is None:
            return jsonify({'error': 'access denied'})

        if args['title']:
            if len(args['title']) > 80:
                return jsonify({'error': 'wrong len of title'})
            book.title = args['title']

        if args['author']:
            if len(args['title']) > 80:
                return jsonify({'error': 'wrong len of author'})
            book.author = args['author']

        if args['description']:
            if len(args['description']) > 1000:
                return jsonify({'error': 'wrong len of description'})
            book.description = args['description']

        if args['genre_id']:
            genre = dbhelper.Genre.query.filter_by(id=args['genre_id']).first()
            if genre is None:
                return jsonify({'error': 'wrong genre'})
            genre.books.append(book)
            book.genre_id = genre.id

        if args['file'] and args['file_format']:
            if args['file_format'] not in ALLOWED_BOOKS_EXTENSIONS:
                return jsonify({'error': 'wrong file_format'})
            path = os.path.join(app.config['UPLOAD_FOLDER'], str(book.id))

            if os.path.exists(book.file):
                os.remove(book.file)

            book.file = os.path.join(path,
                                     functions.transliterate('_'.join(book.title.split())) + '.' +
                                     args['file_format'])
            with open(book.file, 'wb') as f:
                f.write(b64decode(args['file']))
        elif args['file'] or args['file_format']:
            return jsonify({'error': 'file or file_format missed'})

        if args['image'] and args['image_format']:
            if args['image_format'] not in ALLOWED_IMAGES_EXTENSIONS:
                return jsonify({'error': 'wrong image_format'})
            path = os.path.join(app.config['UPLOAD_FOLDER'], str(book.id))

            if os.path.exists(book.image):
                os.remove(book.image)

            book.image = os.path.join(path, 'image.' + args['image_format'])
            with open(book.image, 'wb') as img:
                img.write(b64decode(args['image']))
        elif args['image'] or args['image_format']:
            return jsonify({'error': 'image or image_format missed'})

        dbhelper.db.session.commit()
        return jsonify({'success': 'OK'})


class BooksListApi(Resource):
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('token', required=True)
    post_parser.add_argument('title', required=True)
    post_parser.add_argument('author', required=True)
    post_parser.add_argument('genre_id', required=True, type=int)
    post_parser.add_argument('description', required=True)
    post_parser.add_argument('file', required=True)
    post_parser.add_argument('file_format', required=True)
    post_parser.add_argument('image', required=True)
    post_parser.add_argument('image_format', required=True)

    get_parser = reqparse.RequestParser()
    get_parser.add_argument('sorting', required=True)
    get_parser.add_argument('genre_id', type=int)

    def get(self):  # Список книг с сортировкой и фильтрацией по жанрам
        args = BooksListApi.get_parser.parse_args()
        sorting_dict = {key: val for val, key in SORT_BOOKS}
        if args['sorting'] not in sorting_dict:
            return jsonify({'error': f'sorting must be {" | ".join(sorting_dict)}'})
        if args['genre_id'] is not None:
            genre = dbhelper.Genre.query.filter_by(id=args['genre_id']).first()
            if genre is None:
                return jsonify({'error': 'wrong genre_id'})
            books = functions.get_sorted_books(sorting_dict[args['sorting']],
                                               genre_id=args['genre_id'])
        else:
            books = functions.get_sorted_books(sorting_dict[args['sorting']])
        return jsonify({'books': [{'id': book.id, 'title': book.title, 'author': book.author,
                                   'genre_id': book.genre_id, 'likes': book.likes,
                                   'comments': book.comments} for book in books]})

    def post(self):  # Добавить книгу
        args = BooksListApi.post_parser.parse_args()
        if args['token'] is None or args['token'] not in tokens_ids:
            return jsonify({'error': 'access denied'})
        if len(args['title']) > 80 or len(args['author']) > 80 or len(args['description']) > 1000 \
                or dbhelper.Genre.query.filter_by(id=args['genre_id']).first() is None or \
                args['file_format'] not in ALLOWED_BOOKS_EXTENSIONS or \
                args['image_format'] not in ALLOWED_IMAGES_EXTENSIONS:
            return jsonify({'error': 'wrong len or genre or format'})

        book = dbhelper.Book(title=args['title'], author=args['author'], genre_id=args['genre_id'],
                             description=args['description'])
        user = dbhelper.User.query.filter_by(id=tokens_ids[args['token']]).first()
        user.books.append(book)
        genre = dbhelper.Genre.query.filter_by(id=args['genre_id']).first()
        genre.books.append(book)
        dbhelper.db.session.commit()

        book = dbhelper.Book.query.filter_by(title=args['title']).first()
        # path = app.config['UPLOAD_FOLDER'] + str(book.id)
        path = os.path.join(app.config['UPLOAD_FOLDER'], str(book.id))
        os.mkdir(path)

        book.image = os.path.join(path, 'image.' + args['image_format'])
        with open(book.image, 'wb') as img:
            img.write(b64decode(args['image']))

        book.file = os.path.join(path, functions.transliterate(
            '_'.join(book.title.split())) + '.' + args['file_format'])
        with open(book.file, 'wb') as f:
            f.write(b64decode(args['file']))
        dbhelper.db.session.commit()

        return jsonify({'success': 'OK'})


class UserApi(Resource):
    delete_parser = reqparse.RequestParser()
    delete_parser.add_argument('token', required=True)
    put_parser = delete_parser.copy()
    put_parser.add_argument('status', required=True)

    def get(self, user_id):  # Информация о пользователе
        user = abort_if_user_not_found(user_id)
        books = dbhelper.Book.query.filter_by(uploader_id=user_id).order_by(
            dbhelper.Book.id.desc()).all()
        return jsonify({'user': {'id': user.id, 'username': user.username,
                                 'status': functions.get_status(user_id),
                                 'upload': dbhelper.Book.query.filter_by(
                                     uploader_id=user_id).count(),
                                 'liked': functions.get_user_likes(user_id),
                                 'likes': dbhelper.Like.query.filter_by(user_id=user_id).count(),
                                 'commented': functions.get_user_comments(user_id)},
                        'books': [{'id': book.id, 'title': book.title, 'author': book.author,
                                   'genre_id': book.genre_id} for book in books]})

    def delete(self, user_id):  # Бан пользователя
        args = UserApi.delete_parser.parse_args()
        if dbhelper.Admin.query.filter_by(user_id=tokens_ids.get(args['token'])).first() is None:
            return jsonify({'error': 'access denied'})
        user = abort_if_user_not_found(user_id)
        functions.ban_user(user_id)
        return jsonify({'success': 'OK'})

    def put(self, user_id):  # Изменить статус пользователя
        args = UserApi.put_parser.parse_args()
        if dbhelper.Admin.query.filter_by(user_id=tokens_ids.get(args['token'])).first() is None:
            return jsonify({'error': 'access denied'})
        user = abort_if_user_not_found(user_id)
        if args['status'] not in {'Пользователь', 'Модератор', 'Администратор'}:
            return jsonify({'error': 'status must be Пользователь | Модератор | Администратор'})
        functions.change_status(user_id, args['status'])
        return jsonify({'success': 'OK'})


class UsersListApi(Resource):
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('action', required=True)
    post_parser.add_argument('username', required=True)
    post_parser.add_argument('password', required=True)

    get_parser = reqparse.RequestParser()
    get_parser.add_argument('criterion', required=True)

    def get(self):
        args = UsersListApi.get_parser.parse_args()
        tops = {'upload': functions.get_upload_top, 'liked': functions.get_liked_top,
                'likes': functions.get_likes_top, 'commented': functions.get_commented_top}
        if args['criterion'] in tops:
            return jsonify({'users': tops[args['criterion']]()[:100]})
        return jsonify({'error': 'criterion must be upload | liked | likes | commented'})

    def post(self):  # Логин/регистрация
        args = UsersListApi.post_parser.parse_args()
        if not (6 <= len(args['username']) <= 32 and 6 <= len(args['password']) <= 32):
            return jsonify({'error': 'login or password have the wrong length'})
        if args['action'] == 'register':
            if dbhelper.User.query.filter_by(username=args['username']).first() is not None:
                return jsonify({'error': 'user "{}" already exists'.format(args['username'])})
            user = dbhelper.User(username=args['username'],
                                 password_hash=generate_password_hash(args['password']))
            dbhelper.db.session.add(user)
            dbhelper.db.session.commit()
            user = dbhelper.User.query.filter_by(username=args['username']).first()
        elif args['action'] == 'login':
            user = dbhelper.User.query.filter_by(username=args['username']).first()
            if user is None or not check_password_hash(user.password_hash, args['password']):
                return jsonify({'error': 'wrong login or password'})
        else:
            abort(404, message="wrong action {}".format(args['action']))

        return jsonify({'success': 'OK', 'token': generate_token(user.id)})


def abort_if_book_not_found(book_id):
    book = dbhelper.Book.query.filter_by(id=book_id).first()
    if book:
        return book
    abort(404, message="Book {} not found".format(book_id))


def abort_if_user_not_found(user_id):
    user = dbhelper.User.query.filter_by(id=user_id).first()
    if user:
        return user
    abort(404, message="User {} not found".format(user_id))


api = Api(app, catch_all_404s=True)
api.add_resource(BooksListApi, '/api/books')  # для списка объектов
api.add_resource(BooksApi, '/api/books/<int:book_id>')  # для одного объекта

api.add_resource(UsersListApi, '/api/users')
api.add_resource(UserApi, '/api/users/<int:user_id>')
