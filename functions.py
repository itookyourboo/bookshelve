from constants import db, STATUSES
from dbhelper import *
import shutil
from werkzeug.security import generate_password_hash, \
    check_password_hash


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


# Бан пользователя и его книг
def ban_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    books = Book.query.filter_by(uploader_id=user_id).all()
    db.session.delete(user)
    for book in books:
        db.session.delete(book)
        shutil.rmtree(f'static/books/{book.id}', ignore_errors=True)
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