import functions
from dbhelper import *
from constants import *

from flask import Flask, session, send_from_directory, send_file
from flask import request, redirect, url_for, render_template
# from forms import LoginForm, RegisterForm, AddBookForm, StatusForm
from forms import *
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import os
from functions import transliterate, like


@app.route('/')
@app.route('/books')
def index():
    books = Book.query.order_by(Book.id.desc()).all()
    for book in books:
        if not book.image:
            book.image = 'static/placeholder_book.jpg'
        book.likes = functions.get_likes(book.id)
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


@app.route('/books/add', methods=['GET', 'POST'])
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
                # path = app.config['UPLOAD_FOLDER'] + str(book.id)
                path = os.path.join(app.config['UPLOAD_FOLDER'], str(book.id))
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


@app.route('/books/<int:book_id>', methods=['GET', 'POST'])
def get_book(book_id):
    book = Book.query.filter_by(id=book_id).first()
    print(book.uploader)

    if request.method == 'POST':
        if 'user_id' in session:
            if 'download' in request.form:
                return send_file(book.file, as_attachment=True)
            elif 'like' in request.form:
                like(session['user_id'], book_id)
        else:
            return redirect('/login')
    return render_template('book.html', title=book.title, book=book,
                           is_liked=bool(Like.query.filter_by(user_id=session['user_id'],
                                                              book_id=book_id).first()))


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    status_form = StatusForm()
    ban_form = BanForm()
    info_form = InfoForm()

    if status_form.status_submit.data and status_form.validate_on_submit():
        id = status_form.status_field.data
        user = User.query.filter_by(id=id).first()
        status_message = 'Пользователь не существует'
        if user:
            functions.change_status(id, status_form.status_select.data)
            status_message = 'Статус успешно изменён'
        return render_template('admin.html', title='ADMIN',
                               status_form=status_form, ban_form=ban_form, info_form=info_form,
                               status_message=status_message)

    if ban_form.ban_submit.data and ban_form.validate_on_submit():
        id = ban_form.ban_field.data
        user = User.query.filter_by(id=id).first()
        ban_message = 'Пользователь не существует'
        if user:
            functions.ban_user(id)
            ban_message = 'Пользователь забанен/удалён'

        return render_template('admin.html', title='ADMIN',
                               status_form=status_form, ban_form=ban_form, info_form=info_form,
                               ban_message=ban_message)

    if info_form.info_submit and info_form.validate_on_submit():
        id = info_form.info_field.data
        user = User.query.filter_by(id=id).first()
        info_message = 'Пользователь не существует'
        if user:
            status = user.status
            books = Book.query.filter_by(uploader_id=id).count()
            likes = Like.query.filter_by(user_id=id).count()
            username, books_count = user.username, books

            info_message = f"ID{id}: {username} ({status}).<br>Загрузил книг: {books_count}<br>Поставил лайков: {likes}"

        return render_template('admin.html', title='ADMIN',
                               status_form=status_form, ban_form=ban_form, info_form=info_form,
                               info_message=info_message)

    return render_template('admin.html', title='ADMIN',
                           status_form=status_form, ban_form=ban_form, info_form=info_form)


if __name__ == '__main__':
    app.run(port=8000, host='127.0.0.1')
