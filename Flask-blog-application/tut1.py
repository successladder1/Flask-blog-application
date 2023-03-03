from flask import Flask, render_template, request
app=Flask(__name__)
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

current_dir=os.path.abspath(os.path.dirname(__file__))
app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///" + os.path.join(current_dir, "myblogdb.sqlite3")
db=SQLAlchemy()
db.init_app(app)
app.app_context().push()

class Contacts(db.Model):
    contact_id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String, nullable=False)
    email=db.Column(db.String, nullable=False)
    phone_num=db.Column(db.String, nullable=False)
    mes=db.Column(db.String, nullable=False)
    date=db.Column(db.String, nullable=True)

class Posts(db.Model):
    post_id=db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String, nullable=False)
    content=db.Column(db.String, nullable=False)
    posted_by=db.Column(db.String, nullable=False)
    slug=db.Column(db.String, nullable=False)
    date=db.Column(db.String, nullable=True)
    img_file=db.Column(db.String, nullable=True)

@app.route("/")
def home():
    posts = Posts.query.filter_by().all()
    return render_template("index.html", posts=posts)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method=="POST":
        #add entry to database
        name=request.form.get('name')
        email=request.form.get('email')
        phone_num=request.form.get('phone_num')
        mes=request.form.get('message')
        entry=Contacts(name=name,email=email ,phone_num=phone_num, mes=mes, date=datetime.now())
        db.session.add(entry)
        db.session.commit()
    return render_template("contact.html")

@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post=Posts.query.filter_by(slug=post_slug).first()
    return render_template("post.html", post=post)

if __name__=="__main__":
    app.run(debug=True)