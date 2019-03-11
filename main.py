from sqlalchemy import func

import functions
from dbhelper import *
from constants import *
from db_base import add_all

from flask import session, send_file
from flask import request, redirect, url_for, render_template
from forms import *
from werkzeug.security import check_password_hash, generate_password_hash
import os
from functions import transliterate, like, get_sorted_books, get_searched_books


add_all()


@app.route('/', methods=['GET', 'POST'])
@app.route('/books', methods=['GET', 'POST'])
def index():
    form = SortForm(sorting=SORT_DEFAULT[0])
    search_form = SearchForm()
    books = get_sorted_books(form.sorting.data)

    if request.method == 'POST':
        if form.sort.data:
            books = get_sorted_books(form.sorting.data)
            return render_template('index.html', title=TITLE, session=session,
                                   books=books, columns=app.config['BOOKS_COLUMNS'], sort_form=form,
                                   genres=get_genres(), index_title='Все книги', search_form=search_form)

        if search_form.search.data:
            books = get_searched_books(search_form.field.data)
            print(books)
            return render_template('index.html', title=TITLE, session=session,
                                   books=books, columns=app.config['BOOKS_COLUMNS'], sort_form=form,
                                   genres=get_genres(), index_title='Все книги', search_form=search_form)

    return render_template('index.html', title=TITLE, session=session,
                           books=books, columns=app.config['BOOKS_COLUMNS'], sort_form=form,
                           genres=get_genres(), index_title='Все книги', search_form=search_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            session.clear()
            session['username'] = user.username
            session['user_id'] = user.id
            return redirect('/')
        form.submit.errors.append('Неправильный логин или пароль')
    return render_template('login.html', title='Вход', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first() is None:
            user = User(username=form.username.data,
                        password_hash=generate_password_hash(form.password.data))
            db.session.add(user)
            db.session.commit()

            user = User.query.filter_by(username=form.username.data).first()
            session.clear()
            session['username'] = user.username
            session['user_id'] = user.id
            return redirect('/')
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
    form.genre.choices = [(genre.id, genre.name) for genre in get_genres()]
    if form.validate_on_submit():
        img_name, file_name = form.image.data.filename, form.file.data.filename
        if '.' in img_name and '.' in file_name:
            img_ext = img_name.rsplit('.', 1)[1].lower()
            file_ext = file_name.rsplit('.', 1)[1].lower()
            if img_ext in ALLOWED_IMAGES_EXTENSIONS and file_ext in ALLOWED_BOOKS_EXTENSIONS:
                book = Book(title=form.title.data, author=form.author.data,
                            genre_id=form.genre.data, description=form.description.data)
                user = User.query.filter_by(id=session['user_id']).first()
                user.books.append(book)
                genre = Genre.query.filter_by(id=form.genre.data).first()
                genre.books.append(book)
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
                return redirect('/')

            form.submit.errors.append('Запрещенный формат файла')
        form.submit.errors.append('Имена файлов должны содержать расширение')

    return render_template('add_book.html', title='Добавить книгу', form=form)


@app.route('/books/<int:book_id>', methods=['GET', 'POST'])
def get_book(book_id):
    book = Book.query.filter_by(id=book_id).first()

    if request.method == 'POST':
        if 'user_id' in session:
            if 'download' in request.form:
                return send_file(book.file, as_attachment=True)
            elif 'like' in request.form:
                like(session['user_id'], book_id)
        else:
            return redirect('/login')

    moder, is_liked = False, False
    if 'user_id' in session:
        is_liked = bool(Like.query.filter_by(book_id=book_id, user_id=session['user_id']).first())
        moder = Moder.query.filter_by(user_id=session['user_id']).first() or book.uploader_id == session['user_id']

    return render_template('book.html', title=book.title, book=book,
                           is_liked=is_liked, moder=moder)


@app.route('/books/edit/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    if not functions.can_edit(session, book_id):
        return redirect('/')

    book = Book.query.filter_by(id=book_id).first()
    form = EditBookForm(title=book.title, author=book.author, description=book.description, genre=book.genre_id)
    form.genre.choices = [(genre.id, genre.name) for genre in get_genres()]

    if form.validate_on_submit():
        if form.image.data:
            img_name = form.image.data.filename
            if '.' in img_name:
                img_ext = img_name.rsplit('.', 1)[1].lower()
                if img_ext in ALLOWED_IMAGES_EXTENSIONS:
                    path = os.path.join(app.config['UPLOAD_FOLDER'], str(book.id))

                    if os.path.exists(book.image):
                        os.remove(book.image)

                    book.image = os.path.join(path, 'image.' + img_ext)
                    with open(book.image, 'wb') as img:
                        img.write(request.files[form.image.name].read())

                form.submit.errors.append('Запрещенный формат файла')
            form.submit.errors.append('Имена файлов должны содержать расширение')

        if form.file.data:
            file_name = form.file.data.filename
            if '.' in file_name:
                file_ext = file_name.rsplit('.', 1)[1].lower()
                if file_ext in ALLOWED_BOOKS_EXTENSIONS:
                    path = os.path.join(app.config['UPLOAD_FOLDER'], str(book.id))

                    if os.path.exists(book.file):
                        os.remove(book.file)

                    book.file = os.path.join(path, transliterate(
                        '_'.join(book.title.split())) + '.' + file_ext)
                    with open(book.file, 'wb') as f:
                        f.write(request.files[form.file.name].read())

                form.submit.errors.append('Запрещенный формат файла')
            form.submit.errors.append('Имена файлов должны содержать расширение')

        if form.title.data:
            book.title = form.title.data
        if form.author.data:
            book.author = form.author.data
        if form.author.data:
            book.description = form.description.data
        if form.genre.data:
            genre = Genre.query.filter_by(id=form.genre.data).first()
            genre.books.append(book)
            book.genre_id = genre.id

        db.session.add(book)
        db.session.commit()

        return redirect(f'/books/{book.id}')

    return render_template('edit_book.html', title='Редактирование книги', form=form)


@app.route('/books/delete/<int:book_id>')
def delete_book(book_id):
    if functions.can_edit(session, book_id):
        functions.delete_book(book_id)

    return redirect('/')


@app.route('/books/genre/<int:genre_id>', methods=['GET', 'POST'])
def books_genre(genre_id):
    genre_name = Genre.query.filter_by(id=genre_id).first().name
    form = SortForm(sorting=SORT_DEFAULT[0])
    search_form = SearchForm()
    books = get_sorted_books(form.sorting.data, genre_id=genre_id)

    if request.method == 'POST':
        if form.sort.data:
            books = get_sorted_books(form.sorting.data, genre_id=genre_id)
            return render_template('index.html', title=TITLE, session=session,
                                   books=books, columns=app.config['BOOKS_COLUMNS'], sort_form=form,
                                   genres=get_genres(), index_title=genre_name, search_form=search_form)
        if search_form.search.data:
            books = get_searched_books(search_form.field.data, genre_id=genre_id)
            return render_template('index.html', title=TITLE, session=session,
                                   books=books, columns=app.config['BOOKS_COLUMNS'], sort_form=form,
                                   genres=get_genres(), index_title=genre_name, search_form=search_form)

    return render_template('index.html', title=TITLE, session=session,
                           books=books, columns=app.config['BOOKS_COLUMNS'], sort_form=form,
                           genres=get_genres(), index_title=genre_name, search_form=search_form)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not functions.is_admin(session):
        return redirect('/')

    status_form = StatusForm()
    ban_form = BanForm()
    info_form = InfoForm()

    if status_form.status_submit.data and status_form.validate_on_submit():
        id = status_form.status_field.data
        user = User.query.filter_by(id=id).first()
        status_message = 'Пользователь не существует'
        if user:
            status_message = functions.change_status(id, status_form.status_select.data)
        return render_template('admin.html', title='ADMIN',
                               status_form=status_form, ban_form=ban_form, info_form=info_form,
                               status_message=status_message)

    if ban_form.ban_submit.data and ban_form.validate_on_submit():
        id = ban_form.ban_field.data
        user = User.query.filter_by(id=id).first()
        ban_message = 'Пользователь не существует'
        if user:
            ban_message = functions.ban_user(id)

        return render_template('admin.html', title='ADMIN',
                               status_form=status_form, ban_form=ban_form, info_form=info_form,
                               ban_message=ban_message)

    if info_form.info_submit and info_form.validate_on_submit():
        id = info_form.info_field.data
        user = User.query.filter_by(id=id).first()
        info_message = 'Пользователь не существует'
        if user:
            info_message = functions.get_info(id)

        return render_template('admin.html', title='ADMIN',
                               status_form=status_form, ban_form=ban_form, info_form=info_form,
                               info_message=info_message)

    return render_template('admin.html', title='ADMIN',
                           status_form=status_form, ban_form=ban_form, info_form=info_form)


@app.route('/admin/users')
def admin_user():
    if not functions.is_admin(session):
        return redirect('/')

    info_list = [functions.get_info(user.id) for user in User.query.all()]
    return render_template('admin_users.html', title="ADMIN USERS",
                           info_list=info_list)


@app.route('/users/<int:user_id>')
def user(user_id):
    user = User.query.filter_by(id=user_id).first()
    books = Book.query.filter_by(uploader_id=user_id).order_by(Book.id.desc()).all()
    for book in books:
        if not book.image:
            book.image = 'static/placeholder_book.jpg'
        book.likes = functions.get_likes(book.id)

    return render_template('user_info.html', title=user.username, info=functions.get_info(user_id),
                           books=books, columns=app.config['BOOKS_COLUMNS'])


@app.route('/top')
def top():
    return render_template('top.html', title='Топ пользователей',
                           upload_list=functions.get_upload_top(),
                           liked_list=functions.get_liked_top(),
                           likes_list=functions.get_likes_top())


if __name__ == '__main__':
    app.run(port=8000, host='127.0.0.1')
