from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, IntegerField, \
    SelectField
from wtforms.validators import DataRequired, EqualTo, Length
from flask_wtf.file import FileField, FileAllowed, FileRequired
from constants import *
from functions import get_genres


class LoginForm(FlaskForm):  # Форма входа
    username = StringField('Логин', validators=[
        DataRequired(message='Поле обязательно для заполнения'),
        Length(min=6, max=32, message='Логин должен быть длиной от 6 до 32 символов')])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Поле обязательно для заполнения'),
        Length(min=8, max=32, message='Пароль должен быть длиной от 8 до 32 символов')])
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):  # Форма регистрации
    username = StringField('Логин', validators=[
        DataRequired(message='Поле обязательно для заполнения'),
        Length(min=6, max=32, message='Логин должен быть длиной от 6 до 32 символов')])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Поле обязательно для заполнения'),
        EqualTo('confirmation', message='Пароли должны совпадать'),
        Length(min=8, max=32, message='Пароль должен быть длиной от 8 до 32 символов')])
    confirmation = PasswordField('Подтвердите пароль', validators=[
        DataRequired(message='Поле обязательно для заполнения'),
        Length(min=8, max=32, message='Пароль должен быть длиной от 8 до 32 символов')])
    submit = SubmitField('Зарегистрироваться')


class AddBookForm(FlaskForm):  # Форма добавления книги
    title = StringField('Название', validators=[
        DataRequired(message='Поле обязательно для заполнения'),
        Length(max=80, message='Название должно быть не длинее 80 символов')])

    author = StringField('Автор', validators=[
        DataRequired(message='Поле обязательно для заполнения'),
        Length(max=80, message='Имя автора должно быть не длиннее 80 символов')])

    description = TextAreaField('Описание книги', validators=[
        DataRequired(message='Поле обязательно для заполнения'),
        Length(max=1000, message='Описание должно быть не длинее 1000 символов')])

    genre = SelectField('Жанр', coerce=int)

    image = FileField('Обложка', validators=[
        FileRequired('Поле обязательно для заполнения'),
        FileAllowed(list(ALLOWED_IMAGES_EXTENSIONS),
                    'Неподдерживаемый формат изображения')
    ])
    file = FileField('Книга', validators=[
        FileRequired('Поле обязательно для заполнения'),
        FileAllowed(list(ALLOWED_BOOKS_EXTENSIONS),
                    'Неподдерживаемый формат книги')
    ])

    submit = SubmitField('Загрузить')


class EditBookForm(FlaskForm):  # Форма редактирования книги
    title = StringField('Название', validators=[
        Length(max=80, message='Название должно быть не длинее 80 символов')])

    author = StringField('Автор', validators=[
        Length(max=80, message='Имя автора должно быть не длиннее 80 символов')])

    description = TextAreaField('Описание книги', validators=[
        Length(max=1000, message='Описание должно быть не длинее 1000 символов')])

    genre = SelectField('Жанр', coerce=int)

    image = FileField('Обложка', validators=[
        FileAllowed(list(ALLOWED_IMAGES_EXTENSIONS),
                    'Неподдерживаемый формат изображения')
    ])
    file = FileField('Книга', validators=[
        FileAllowed(list(ALLOWED_BOOKS_EXTENSIONS),
                    'Неподдерживаемый формат книги')
    ])

    submit = SubmitField('Редактировать')


class StatusForm(FlaskForm):  # Администраторская форма изменения статуса пользователей
    status_field = IntegerField('ID', validators=[
        DataRequired(message='Поле обязательно для заполнения')])
    status_select = SelectField(choices=[(a, a) for a in list(STATUSES.values())])
    status_submit = SubmitField('OK')


class BanForm(FlaskForm):  # Администраторская форма бана пользователей
    ban_field = IntegerField('ID',
                             validators=[DataRequired(message='Поле обязательно для заполнения')])
    ban_submit = SubmitField('OK')


class InfoForm(FlaskForm):  # Администраторская форма удобного получения информации о пользователе
    info_field = IntegerField('ID',
                              validators=[DataRequired(message='Поле обязательно для заполнения')])
    info_submit = SubmitField('OK')


class SortForm(FlaskForm):  # Форма сортировки в шапке
    sorting = SelectField('Сортировка', choices=SORT_BOOKS)
    sort = SubmitField('Сортировать')


class SearchForm(FlaskForm):  # Форма поиска в шапке
    field = StringField('Поиск')
    search = SubmitField('Найти')


class CommentForm(FlaskForm):  # Форма для создания и редактирования комментариев
    field = TextAreaField('Оставить комментарий', validators=[
        Length(min=20, message='Комментарий должен быть не короче 20 символов')
    ])
    submit = SubmitField('ОК')
