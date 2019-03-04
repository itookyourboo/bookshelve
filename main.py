from dbhelper import *
from models import *
from constants import *
from flask import Flask
from flask import request, redirect, url_for

db = DB()
db.connect()

app = Flask(__name__)

genreModel = GenreModel(db.get_connection())
genreModel.init_table()


@app.route("/genres_list")
def genres_list():
    return "<br>".join([str(genre[0]) + " " + genre[1] for genre in genreModel.get_all()])


@app.route("/genres_delete/<int:id>")
def genres_delete(id):
    genreModel.delete(id)
    return redirect(url_for('genres_list'))


@app.route("/genres_add/<name>")
def genres_add(name):
    genreModel.insert(Genre(None, name))
    return redirect(url_for('genres_list'))


if __name__ == '__main__':
    app.run(port=8000, host='127.0.0.1')