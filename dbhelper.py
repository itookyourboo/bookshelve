from constants import db


# Модель пользователя
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(160), nullable=False)

    def __repr__(self):
        return f'User ID{self.id}. {self.username}'


# Модель книги
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    author = db.Column(db.String(80), nullable=False)

    genre_id = db.Column(db.Integer,
                         db.ForeignKey('genre.id'),
                         nullable=False)
    genre = db.relationship('Genre', backref=db.backref('books', lazy=True))

    description = db.Column(db.String(1000), nullable=False)

    uploader_id = db.Column(db.Integer,
                            db.ForeignKey('user.id'),
                            nullable=False)
    uploader = db.relationship('User', backref=db.backref('books', lazy=True))
    image = db.Column(db.String(200))
    file = db.Column(db.String(200))

    likes = 0
    comments = 0


# Модель автора
class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    image = db.Column(db.String(80))
    description = db.Column(db.String(1000))


# Модель модератора
class Moder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


# Модель админа
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


# Модель жанра
class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))


# Модель лайка
class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)


# Комментарий
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('comments', lazy=True))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    text = db.Column(db.String(1000))

    can_delete = False
    can_edit = False


db.create_all()