from sqlalchemy import func

from constants import db, STATUSES, SORT_DEFAULT
from dbhelper import *
import shutil
from functools import reduce


# Проверка на админа
def is_admin(session):
    return 'user_id' in session and Admin.query.filter_by(user_id=session['user_id']).first()


# Проверка на модератора
def is_moder(session):
    return 'user_id' in session and Moder.query.filter_by(user_id=session['user_id']).first()


def can_edit(session, book_id):
    if not 'user_id' in session:
        return False
    return is_moder(session) or Book.query.filter_by(id=book_id, uploader_id=session['user_id']).first()


# Изменить статус пользователя (пользователь, модератор, администратор)
def change_status(user_id, status):
    moder = Moder.query.filter_by(user_id=user_id).first()
    admin = Admin.query.filter_by(user_id=user_id).first()

    if admin:
        if admin.id != 1:
            return 'Вы не можете изменить должность главного администратора'

        if status == STATUSES['moder']:
            db.session.delete(admin)
            db.session.commit()
        elif status == STATUSES['user']:
            db.session.delete(admin)
            db.session.delete(moder)
            db.session.commit()
        return 'Статус изменён'

    if moder:
        if status == STATUSES['user']:
            db.session.delete(moder)
            db.session.commit()
        elif status == STATUSES['admin']:
            db.session.add(Admin(user_id=user_id))
            db.session.commit()
        return 'Статус изменён'

    if not admin and not moder:
        if status == STATUSES['moder']:
            db.session.add(Moder(user_id=user_id))
            db.session.commit()
        elif status == STATUSES['admin']:
            db.session.add(Moder(user_id=user_id))
            db.session.add(Admin(user_id=user_id))
            db.session.commit()
        return 'Статус изменён'

    return 'непонел'


# Статус пользователя
def get_status(user_id):
    moder = Moder.query.filter_by(user_id=user_id).first()
    admin = Admin.query.filter_by(user_id=user_id).first()
    if admin:
        return STATUSES['admin']
    if moder:
        return STATUSES['moder']
    return STATUSES['user']


# Информация о пользователе
def get_info(user_id):
    user = User.query.filter_by(id=user_id).first()
    moder = Moder.query.filter_by(user_id=user_id).first()
    admin = Admin.query.filter_by(user_id=user_id).first()
    status = get_status(user_id)
    if admin:
        status += f"_{admin.id}"

    books = Book.query.filter_by(uploader_id=user_id).count()
    likes = Like.query.filter_by(user_id=user_id).count()
    liked = get_user_likes(user_id)
    username, books_count = user.username, books

    return f"ID{user_id}: {username} ({status}).<br>Загрузил книг: {books_count}<br>" \
           f"Получил лайков: {liked}<br>Поставил лайков: {likes}"


# Бан пользователя, его книг и лайков
def ban_user(user_id):
    if user_id == 1:
        return 'Вы не можете забанить главного администратора'

    moder = Moder.query.filter_by(user_id=user_id).first()
    admin = Moder.query.filter_by(user_id=user_id).first()
    user = User.query.filter_by(id=user_id).first()
    books = Book.query.filter_by(uploader_id=user_id).all()
    db.session.delete(user)
    if moder:
        db.session.delete(moder)
    if admin:
        db.session.delete(admin)

    for book in books:
        db.session.delete(Like.query.filter_by(user_id=user_id, book_id=book.id).first())
        db.session.delete(book)
        shutil.rmtree(f'static/books/{book.id}', ignore_errors=True)
    db.session.commit()

    return 'Пользователь успешно забанен'


def user_exists(username):
    return bool(User.query.filter_by(username=username).first())


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


def get_genres():
    return Genre.query.order_by(Genre.name.asc()).all()


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


def transliterate(string):
    capital_letters = {'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E',
                       'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N',
                       'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F',
                       'Х': 'H', 'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', }
    capital_letters_transliterated_to_multiple_letters = {'Ж': 'Zh', 'Ц': 'Ts', 'Ч': 'Ch',
                                                          'Ш': 'Sh', 'Щ': 'Sch', 'Ю': 'Yu',
                                                          'Я': 'Ya', }
    lower_case_letters = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
                          'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
                          'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
                          'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '',
                          'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya', }
    capital_and_lower_case_letter_pairs = {}
    for capital_letter, capital_letter_translit in \
            capital_letters_transliterated_to_multiple_letters.items():
        for lowercase_letter, lowercase_letter_translit in lower_case_letters.items():
            capital_and_lower_case_letter_pairs[
                "%s%s" % (capital_letter, lowercase_letter)] = "%s%s" % (
                capital_letter_translit, lowercase_letter_translit)
    for dictionary in (capital_and_lower_case_letter_pairs, capital_letters, lower_case_letters):
        for cyrillic_string, latin_string in dictionary.items():
            string = string.replace(cyrillic_string, latin_string)
    for cyrillic_string, latin_string in capital_letters_transliterated_to_multiple_letters.items():
        string = string.replace(cyrillic_string, latin_string.upper())
    return string


# Удаление книги и лайков на ней
def delete_book(book_id):
    book = Book.query.filter_by(id=book_id).first()
    db.session.query(Like).filter(Like.book_id==book.id).delete()
    db.session.delete(book)
    shutil.rmtree(f'static/books/{book.id}', ignore_errors=True)
    db.session.commit()


# Удаление всех книг
def delete_all_books():
    db.session.query(Book).delete()
    db.session.commit()


def delete_all_genres():
    db.session.query(Genre).delete()
    db.session.commit()


def get_sorted_books(sort, genre_id=None):
    if sort is None or sort == 'None':
        sort = SORT_DEFAULT[0]

    if 'likes' in sort:
        books = (Book.query.filter_by(genre_id=genre_id).all() if genre_id else Book.query.all())
        for book in books:
            if not book.image:
                book.image = 'static/placeholder_book.jpg'
            book.likes = get_likes(book.id)
        books = sorted(books, key=lambda x: (-1 if 'asc' in sort else 1) * x.likes)
        return books

    books = (Book.query.filter_by(genre_id=genre_id).order_by(eval(sort)).all()
             if genre_id else Book.query.order_by(eval(sort)).all())

    for book in books:
        if not book.image:
            book.image = 'static/placeholder_book.jpg'
        book.likes = get_likes(book.id)
    return books


def get_upload_top():
    books = Book.query.with_entities(Book.uploader_id, func.count(Book.uploader_id))\
        .group_by(Book.uploader_id).all()
    return sorted([{
        'user_id': book[0],
        'username': User.query.filter_by(id=book[0]).first().username,
        'count': book[1]
    } for book in books], key=lambda x: -x['count'])


def get_liked_top():
    likes = Like.query.with_entities(Like.user_id, func.count(Like.user_id))\
        .group_by(Like.user_id).all()
    return sorted([{
        'user_id': like[0],
        'username': User.query.filter_by(id=like[0]).first().username,
        'count': like[1]
    } for like in likes], key=lambda x: -x['count'])


def get_likes_top():
    result = {}
    books = Book.query.all()
    for book in books:
        user_id = book.uploader_id
        result[user_id] = get_user_likes(user_id)

    return sorted([{
        'user_id': id,
        'username': User.query.filter_by(id=id).first().username,
        'count': result[id]
    } for id in result], key=lambda x: -x['count'])


def get_user_likes(user_id):
    return reduce(lambda a, x: a + x,
                  [get_likes(book.id) for book in Book.query.filter_by(uploader_id=user_id).all()])