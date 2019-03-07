from flask import jsonify, session, url_for
from flask_restful import reqparse, abort, Api, Resource
import dbhelper
from werkzeug.security import generate_password_hash, check_password_hash
from base64 import b64decode
import os


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
        dbhelper.Book.query.filter_by(id=book_id).delete()
        dbhelper.db.session.commit()
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


        dbhelper.Book.query.filter_by(id=book_id).update(args)
        dbhelper.db.session.commit()
        return jsonify({'success': 'OK'})


class BooksListApi(Resource):
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('title', required=True)
    post_parser.add_argument('description', required=True)
    post_parser.add_argument('file', required=True)
    post_parser.add_argument('format', required=True)

    def get(self):  # В будущем тут можно возвращать недавно добавленные книги
        books = dbhelper.Book.query.all()
        return jsonify({'books': [[book.title] for book in books]})

    def post(self):  # Добавить книгу
        args = BooksListApi.post_parser.parse_args()
        path = f'static/books/{"_".join(args["title"].split())}.{args["format"]}'

        book = dbhelper.Book(title=args['title'], description=args['description'], file=path)
        user = dbhelper.User.query.filter_by(id=session['user_id']).first()
        user.books.append(book)
        with open(path, 'wb') as f:
            f.write(b64decode(args['file']))
        dbhelper.db.session.commit()
        return jsonify({'success': 'OK'})


class UserApi(Resource):
    put_parser = reqparse.RequestParser()
    put_parser.add_argument('password', required=True)

    def get(self, user_id):  # Информация о пользователе. Потом можно будет возвращать загруженные, понравившиеся книги.
        user = abort_if_user_not_found(user_id)
        return jsonify({'user': [user.username, user.status, user.books]})

    def delete(self, user_id):  # Удалить пользователя
        abort_if_user_not_found(user_id)
        dbhelper.User.query.filter_by(id=user_id).delete()
        dbhelper.db.session.commit()
        return jsonify({'success': 'OK'})

    def put(self, user_id):  # Изменить пароль
        abort_if_user_not_found(user_id)
        args = UserApi.put_parser.parse_args()
        dbhelper.User.query.filter_by(id=user_id).update(
            {'password_hash': generate_password_hash(args['password'])})
        dbhelper.db.session.commit()
        return jsonify({'success': 'OK'})


class UsersListApi(Resource):
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('action', required=True)
    post_parser.add_argument('username', required=True)
    post_parser.add_argument('password', required=True)

    def get(self):
        users = dbhelper.User.query.all()
        return jsonify({'users': [[user.id, user.username, len(user.books)] for user in users]})

    def post(self):  # Логин/регистрация
        args = UsersListApi.post_parser.parse_args()
        if args['action'] == 'register':
            if dbhelper.User.query.filter_by(username=args['username']).first() is not None:
                return jsonify({'error': 'user "{}" already exists'.format(args['username'])})
            user = dbhelper.User(username=args['username'],
                                 password_hash=generate_password_hash(args['password']))
            dbhelper.db.session.add(user)
            dbhelper.db.session.commit()
        elif args['action'] == 'login':
            user = dbhelper.User.query.filter_by(username=args['username']).first()
            if user is None or not check_password_hash(user.password_hash, args['password']):
                return jsonify({'error': 'wrong login or password'})
        else:
            abort(404, message="wrong action {}".format(args['action']))
        session['user_id'] = user.id
        session['username'] = user.username
        print(session)
        return jsonify({'success': 'OK'})


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
