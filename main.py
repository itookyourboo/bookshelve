import functions
from dbhelper import *
from constants import *

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired
from flask import Flask
from flask import request, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from requests import get, post, delete, put


session = {}


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    login = SubmitField('Войти')
    logup = SubmitField('Регистрация')


class LogupForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    logup = SubmitField('Регистрация')


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    if 'username' not in session:
        return redirect('/login')

    return render_template('index.html', title=TITLE, session=session)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        is_login_form = form.login.data
        if is_login_form:
            username = form.username.data
            password = form.password.data
            result = functions.login_user(username, password)
            if result[0]:
                session['username'], session['user_id'] = result[1]['username'], result[1]['user_id']
                return redirect('/index')
            return render_template('login.html', error=result[1], title=TITLE, form=form)
        return redirect('/logup')
    return render_template('login.html', title=TITLE, form=form)


@app.route('/logup', methods=['GET', 'POST'])
def logup():
    form = LogupForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        result = functions.logup_user(username, password)
        if result[0]:
            session['username'], session['user_id'] = result[1]['username'], result[1]['user_id']
            return redirect('/index')
        return render_template('logup.html', error=result[1], title=TITLE, form=form)
    return render_template('logup.html', title=TITLE, form=form)


@app.route('/logout')
def logout():
    functions.logout(session)
    return redirect('/index')


if __name__ == '__main__':
    app.run(port=8000, host='127.0.0.1')