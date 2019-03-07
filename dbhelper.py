from constants import db


# Модель пользователя
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80))
    status = db.Column(db.String(80))

    def __repr__(self):
        return f'User ID{self.id}. {self.username}: {self.status}'


# Модель книги
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    author = db.relationship('Author', backref=db.backref('Author', lazy=True))
    genre = db.relationship('Genre', backref=db.backref('Genre', lazy=True))
    description = db.Column(db.String(1000), nullable=False)
    user = db.relationship('User', backref=db.backref('Book', lazy=True))
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