from flask import Flask
from flask import request, render_template
from flask import request, redirect, url_for
from flask import session

from database import articles

app = Flask(__name__)
app.secret_key = b'4\xa1f8a\x04y:\xa9\xc19\xc67M4+\xb5\xb1\xb9S\x92@\xf8\x97'

@app.route('/')
def view_welcome_page():
    return render_template('welcome_page.jinja2', text='si zabil')

@app.route("/about/")
def view_about():
    return render_template("about.jinja2")

@app.route("/articles/")
def view_articles():
    return render_template("articles.jinja2", articles=articles)

@app.route("/articles/<int:art_id>")
def view_article(art_id):
    article = articles.get(art_id)
    if article:
        return render_template("article.jinja2",article=article)
    return render_template("article_not_found.jinja2", art_id=art_id)

@app.route("/admin/")
def view_admin():
    if "logged" not in session:
        return redirect(url_for("view_login"))
    return render_template("admin.jinja2")

@app.route("/login/", methods=["GET"])
def view_login():
    return render_template("login.jinja2")

@app.route("/login/", methods=["POST"])
def login_user():
    username = request.form["username"]
    password = request.form["password"]
    if username == "admin" and password == "admin":
        session["logged"] = True
        return redirect(url_for("view_admin"))
    else:
        return redirect(url_for("view_login"))

@app.route("/logout/", methods=["POST"])
def logout_user():
    session.pop("logged")
    return redirect(url_for("view_welcome_page"))


if __name__ == '__main__':
    app.run(debug=True)