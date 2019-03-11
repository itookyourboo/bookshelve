from constants import *
from dbhelper import *
import functions

from werkzeug.security import generate_password_hash

genres = [
    'Художественная литература',
    'Книги для детей',
    'Образование',
    'Наука и техника',
    'Общество',
    'Деловая литература',
    'Красота. Здоровье. Спорт',
    'Увлечения',
    'Психология',
    'Эзотерика',
    'Философия и религия',
    'Искусство',
    'Подарочные издания',
    'Книги на иностранных языках'
]

ADMINS = [
    ('mainadmin', 'admin007')
]

MODERS = [
    ('moderhino', 'moderhino'),
    ('m0der4tor', 'm0der4tor')
]

USERS = [
    ('useruser', 'useruser'),
    ('user1234', 'user1234'),
    ('polzovatel', 'polzovatel'),
    ('book1love', 'book1love')
]


def add_all():
    add_genres()
    add_users()


def add_genres():
    if len(Genre.query.all()):
        return
    for genre in genres:
        db.session.add(Genre(name=genre))
    db.session.commit()


def add_users():
    [add_admin(name, pswd) for name, pswd in ADMINS]
    [add_moder(name, pswd) for name, pswd in MODERS]
    [add_user(name, pswd) for name, pswd in USERS]


def add_admin(username, password):
    if functions.user_exists(username):
        return

    admin = User(username=username,
                 password_hash=generate_password_hash(password))
    db.session.add(admin)
    db.session.commit()
    functions.change_status(admin.id, STATUSES['admin'])


def add_moder(username, password):
    if functions.user_exists(username):
        return

    moder = User(username=username,
                 password_hash=generate_password_hash(password))
    db.session.add(moder)
    db.session.commit()
    functions.change_status(moder.id, STATUSES['moder'])


def add_user(username, password):
    if functions.user_exists(username):
        return

    user = User(username=username,
                password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
