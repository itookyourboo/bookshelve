from dbhelper import *
from constants import *
from flask import Flask
from flask import request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy


if __name__ == '__main__':
    app.run(port=8000, host='127.0.0.1')