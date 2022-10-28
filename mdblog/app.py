import os
from flask import Flask
from flask import request, render_template
from flask import request, redirect, url_for
from flask import session, flash
from flask import g

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import PasswordField
from wtforms.validators import InputRequired

import sqlite3

from .database import articles

flask_app = Flask(__name__)
flask_app.config.from_pyfile("..\\configs\\default.py")
flask_app.secret_key = b'4\xa1f8a\x04y:\xa9\xc19\xc67M4+\xb5\xb1\xb9S\x92@\xf8\x97'
DATABASE = os.path.join(os.getcwd(),'blog.db')

## FORMS
class LoginForm(FlaskForm):
  username = StringField("Username", validators=[InputRequired()])
  password = PasswordField("Password", validators=[InputRequired()])

class ArticleForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired()])
    content = TextAreaField("Content")

## CONTROLLERS

@flask_app.route('/')
def view_welcome_page():
    return render_template('welcome_page.jinja2', text='si zabil')

@flask_app.route("/about/")
def view_about():
    return render_template("about.jinja2")

## ARTICLES
@flask_app.route("/articles/", methods=["GET"])
def view_articles():
    db = get_db()
    cur = db.execute("SELECT * FROM articles ORDER BY id")
    articles = cur.fetchall()
    return render_template("articles.jinja2", articles=articles)

@flask_app.route("/articles/new/", methods=["GET"])
def view_add_article():
    if "logged" not in session:
        return redirect(url_for("view_login"))

    form = ArticleForm()
    return render_template("article_editor.jinja2", form=form)

@flask_app.route("/articles/", methods=["POST"])
def add_article():
    if "logged" not in session:
        return redirect(url_for("view_login"))

    db = get_db()
    db.execute("INSERT INTO articles (title, content) values (?,?)",[
        request.form.get("title"), request.form.get("content")
    ])
    db.commit()
    return redirect(url_for("view_articles"))

@flask_app.route("/articles/<int:art_id>")
def view_article(art_id):
    db = get_db()
    cur = db.execute("SELECT * FROM articles WHERE id=(?)",[art_id])
    article = cur.fetchone()
    if article:
        return render_template("article.jinja2",article=article)
    return render_template("article_not_found.jinja2", art_id=art_id)

@flask_app.route("/articles/<int:art_id>/edit/", methods=["GET"])
def view_article_editor(art_id):
    if "logged" not in session:
        return redirect(url_for("view_login"))
    db = get_db()
    cur = db.execute("SELECT * FROM articles WHERE id=(?)", [art_id])
    article = cur.fetchone()
    if article:
        form = ArticleForm()
        form.title.data = article["title"]
        form.content.data = article["content"]
        return render_template("article_editor.jinja2", form=form, article=article)

    return render_template("article_not_found.jinja2")

@flask_app.route("/articles/<int:art_id>/edit/", methods=["POST"])
def edit_article(art_id):
    if "logged" not in session:
        return redirect(url_for("view_login"))
    db = get_db()
    cur = db.execute("SELECT * FROM articles WHERE id=(?)", [art_id])
    article = cur.fetchone()
    if article:
        edit_form = ArticleForm(request.form)
        if edit_form.validate():
            db.execute("update articles set title=?, content=? where id=? ",[
                edit_form.title.data, edit_form.content.data, art_id
            ])
            db.commit()
            flash("Edit saved","success")
            return redirect(url_for("view_article", art_id=art_id))
        else:
            for error in edit_form.errors:
                flash("{} is missing".format(error, "alert"))
            return redirect(url_for("view_login"))



@flask_app.route("/admin/")
def view_admin():
    if "logged" not in session:
        return redirect(url_for("view_login"))
    return render_template("admin.jinja2")

@flask_app.route("/login/", methods=["GET"])
def view_login():
    login_form = LoginForm()
    return render_template("login.jinja2", form=login_form)

@flask_app.route("/login/", methods=["POST"])
def login_user():
    #username = request.form["username"]
    #password = request.form["password"]

    login_form = LoginForm(request.form)
    if login_form.validate():
        if login_form.username.data == flask_app.config["USERNAME"] and login_form.password.data == flask_app.config["PASSWORD"]:
            session["logged"] = True
            flash('You were successfully logged in','success')
            return redirect(url_for("view_admin"))
        else:
            flash('Incorrect name or password information', 'alert')
            return render_template("login.jinja2", form=login_form)
    else:
        for error in login_form.errors:
            flash("{} is missing".format(error,"alert"))
        return redirect(url_for("view_login"))

@flask_app.route("/logout/", methods=["POST"])
def logout_user():
    session.pop("logged")
    return redirect(url_for("view_welcome_page"))


##UTILS

def connect_db():
    rv = sqlite3.connect(flask_app.config["DATABASE"])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@flask_app.teardown_appcontext
def close_db(exception):
    if hasattr(g,"sqlite_db"):
        g.sqlite_db.close()

def init_db(app):
    with app.app_context():
        db = get_db()
        with open("mdblog/schema.sql", "r") as fp:
            db.cursor().executescript(fp.read())
        db.commit()