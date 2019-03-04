from constants import *


class User:
    def __init__(self, user_id, name, pswd, status):
        self.user_id, self.name, self.pswd, self.status = user_id, name, pswd, status

    def get_dict(self):
        return {
            KEY_USER_ID: self.user_id,
            KEY_USER_NAME: self.name,
            KEY_USER_PSWD: self.pswd,
            KEY_USER_STATUS_ID: self.status
        }

    def get_tuple(self):
        return self.user_id, self.name, self.pswd, self.status


class Book:
    def __init__(self, book_id, name, author, genre, description, user, image, file):
        self.book_id, self.name, self.author, self.genre, self.user, self.description, \
        self.image, self.file = book_id, name, author, genre, user, description, image, file

    def get_dict(self):
        return {
            KEY_BOOK_ID: self.book_id,
            KEY_BOOK_NAME: self.name,
            KEY_BOOK_AUTHOR_ID: self.author,
            KEY_BOOK_USER_ID: self.user,
            KEY_BOOK_GENRE_ID: self.genre,
            KEY_BOOK_DESCRIPTION: self.description,
            KEY_BOOK_IMAGE: self.image,
            KEY_BOOK_FILE: self.file
        }

    def get_tuple(self):
        return self.book_id, self.name, self.author, self.genre, \
               self.description, self.user, self.image, self.file


class Author:
    def __init__(self, author_id, name, description, image):
        self.author_id, self.name, self.image, self.description = author_id, name, image, description

    def get_dict(self):
        return {
            KEY_AUTHOR_ID: self.author_id,
            KEY_AUTHOR_NAME: self.name,
            KEY_AUTHOR_IMAGE: self.image,
            KEY_AUTHOR_DESCRIPTION: self.description
        }

    def get_tuple(self):
        return self.author_id, self.name, self.image, self.description


class Genre:
    def __init__(self, genre_id, name):
        self.genre_id, self.name = genre_id, name

    def get_dict(self):
        return {
            KEY_GENRE_ID: self.genre_id,
            KEY_GENRE_NAME: self.name
        }

    def get_tuple(self):
        return self.genre_id, self.name


class Status:
    def __init__(self, status_id, name):
        self.status_id, self.name = status_id, name

    def get_dict(self):
        return {
            KEY_STATUS_ID: self.status_id,
            KEY_STATUS_NAME: self.name
        }

    def get_tuple(self):
        return self.status_id, self.name