import functions
from dbhelper import *
from constants import *

from flask import Flask, session
from flask import request, redirect, url_for, render_template
from forms import LoginForm, RegisterForm, AddBookForm
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import os
from functions import transliterate


@app.route('/')
@app.route('/index')
def index():
    books = Book.query.order_by(Book.id.desc()).all()
    for book in books:
        if not book.image:
            book.image = '/static/placeholder_book.jpg'
    return render_template('index.html', title=TITLE, session=session,
                           books=books, columns=app.config['BOOKS_COLUMNS'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            session.clear()
            session['username'] = user.username
            session['user_id'] = user.id
            return redirect('/index')
        form.submit.errors.append('Неправильный логин или пароль')
    return render_template('login.html', title='Вход', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first() is None:
            user = User(username=form.username.data,
                        password_hash=generate_password_hash(form.password.data),
                        status=STATUSES['user'])
            db.session.add(user)
            db.session.commit()

            user = User.query.filter_by(username=form.username.data).first()
            session.clear()
            session['username'] = user.username
            session['user_id'] = user.id
            return redirect('/index')
        form.submit.errors.append('Пользователь с таким логином уже существует')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if 'username' not in session:
        return redirect('/login')

    form = AddBookForm()
    if form.validate_on_submit():
        img_name, file_name = form.image.data.filename, form.file.data.filename
        if '.' in img_name and '.' in file_name:
            img_ext = img_name.rsplit('.', 1)[1].lower()
            file_ext = file_name.rsplit('.', 1)[1].lower()
            if img_ext in ALLOWED_IMAGES_EXTENSIONS and file_ext in ALLOWED_BOOKS_EXTENSIONS:
                book = Book(title=form.title.data, description=form.desc.data)
                user = User.query.filter_by(id=session['user_id']).first()
                user.books.append(book)
                db.session.commit()

                book = Book.query.filter_by(title=form.title.data).first()
                path = app.config['UPLOAD_FOLDER'] + str(book.id)
                # path = os.path.join(app.config['UPLOAD_FOLDER'], str(book.id))
                os.mkdir(path)

                book.image = os.path.join(path, 'image.' + img_ext)
                with open(book.image, 'wb') as img:
                    img.write(request.files[form.image.name].read())

                book.file = os.path.join(path, transliterate(
                    '_'.join(book.title.split())) + '.' + file_ext)
                with open(book.file, 'wb') as f:
                    f.write(request.files[form.image.name].read())
                db.session.commit()
                return redirect('/index')

            form.submit.errors.append('Запрещенный формат файла')
        form.submit.errors.append('Имена файлов должны содержать расширение.')

    return render_template('add_book.html', title='Добавить книгу', form=form)


if __name__ == '__main__':
    app.run(port=8000, host='127.0.0.1')
