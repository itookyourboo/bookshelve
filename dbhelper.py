import sqlite3
from constants import *


class DB:
    def __init__(self):
        self.connection = None

    def connect(self, name="library.db"):
        self.connection = sqlite3.connect(name, check_same_thread=False)

    def get_connection(self):
        return self.connection

    def __del__(self):
        self.connection.close()


class Model:
    def __init__(self, connection, table_name):
        self.connection = connection
        self.table_name = table_name

    def init_table(self):
        pass

    def get(self, id):
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT * FROM {self.table_name} WHERE {KEY_ID} = ?", (str(id)))
        row = cursor.fetchone()
        return row

    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT * FROM {self.table_name}")
        rows = cursor.fetchall()
        return rows

    def insert(self, item):
        params = item.get_tuple()
        cursor = self.connection.cursor()
        cursor.execute(f"INSERT INTO {self.table_name} "
                       f"VALUES({','.join(['?' for i in range(len(params))])})", params)
        cursor.close()
        self.connection.commit()

    def delete(self, id):
        cursor = self.connection.cursor()
        cursor.execute(f"DELETE FROM {self.table_name} WHERE {KEY_ID} = ?", (str(id)))
        cursor.close()
        self.connection.commit()

    def update(self, id, item):
        params = item.get_tuple()
        cursor = self.connection.cursor()
        cursor.execute(f"UPDATE {self.table_name} "
                       f"SET {','.join([a + ' = ?' for a in params])} WHERE {KEY_ID} = ?", *params, id)
        cursor.close()
        self.connection.commit()


class UserModel(Model):
    def __init__(self, connection):
        super().__init__(connection, TABLE_USERS)

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {TABLE_USERS} (
                            {KEY_USER_ID} INTEGER PRIMARY KEY AUTOINCREMENT,
                            {KEY_USER_NAME} VARCHAR(50) NOT NULL,
                            {KEY_USER_PSWD} VARCHAR(128) NOT NULL,
                            {KEY_USER_STATUS_ID} INTEGER NOT NULL)''')
        cursor.close()
        self.connection.commit()


class BookModel(Model):
    def __init__(self, connection):
        super().__init__(connection, TABLE_BOOKS)

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {TABLE_BOOKS} (
                            {KEY_BOOK_ID} INTEGER PRIMARY KEY AUTOINCREMENT,
                            {KEY_BOOK_NAME} VARCHAR(50) NOT NULL,
                            {KEY_BOOK_AUTHOR_ID} INTEGER NOT NULL,
                            {KEY_BOOK_GENRE_ID} INTEGER NOT NULL,
                            {KEY_BOOK_DESCRIPTION} text,
                            {KEY_BOOK_USER_ID} INTEGER NOT NULL,
                            {KEY_BOOK_IMAGE} text,
                            {KEY_BOOK_FILE} text)''')
        cursor.close()
        self.connection.commit()


class AuthorModel(Model):
    def __init__(self, connection):
        super().__init__(connection, TABLE_AUTHORS)

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {TABLE_AUTHORS} (
                            {KEY_AUTHOR_ID} INTEGER PRIMARY KEY AUTOINCREMENT,
                            {KEY_AUTHOR_NAME} VARCHAR(75) NOT NULL,
                            {KEY_AUTHOR_IMAGE} text,
                            {KEY_AUTHOR_DESCRIPTION} text)''')
        cursor.close()
        self.connection.commit()


class GenreModel(Model):
    def __init__(self, connection):
        super().__init__(connection, TABLE_GENRES)

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {TABLE_GENRES} (
                            {KEY_GENRE_ID} INTEGER PRIMARY KEY AUTOINCREMENT,
                            {KEY_GENRE_NAME} text NOT NULL)''')
        cursor.close()
        self.connection.commit()


class StatusModel(Model):
    def __init__(self, connection):
        super().__init__(connection, TABLE_STATUSES)

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {TABLE_STATUSES} (
                            {KEY_STATUS_ID} INTEGER PRIMARY KEY AUTOINCREMENT,
                            {KEY_STATUS_NAME} text NOT NULL)''')
        cursor.close()
        self.connection.commit()