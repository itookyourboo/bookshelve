from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length
from flask_wtf.file import FileField, FileAllowed, FileRequired
from constants import *


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[
        DataRequired(message='Поле обязательно для заполнения'),
        Length(min=6, max=32, message='Логин должен быть длиной от 6 до 32 символов')])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Поле обязательно для заполнения'),
        Length(min=8, max=32, message='Пароль должен быть длиной от 8 до 32 символов')])
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
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


class AddBookForm(FlaskForm):
    title = StringField('Название', validators=[
        DataRequired(message='Поле обязательно для заполнения'),
        Length(max=80, message='Название должно быть не длинее 80 символов')])

    desc = TextAreaField('Описание книги', validators=[
        DataRequired(message='Поле обязательно для заполнения'),
        Length(max=1000, message='Описание должно быть не длинее 1000 символов')])

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
