from constants import db
from dbhelper import *


# Вход в систему
def login_user(username, password):
    userModel = User.query.filter_by(username=username, password=password).first()
    if userModel:
        return {
            'username': username,
            'user_id': userModel.id
        }
    return 'Неверный логин или пароль'


#Регистрация
def logup_user(username, password):
    userModel = User.query.filter_by(username=username).first()
    if userModel:
        return 'Пользователь с таким логином уже существует'
    else:
        user = User(username=username,
                         password=password,
                         status='Пользователь')
        db.session.add(user)
        db.session.commit()
        return {
            'username': username,
            'user_id': user.id
        }


# Выход из системы
def logout(session):
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