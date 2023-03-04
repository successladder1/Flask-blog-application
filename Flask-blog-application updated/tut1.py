from flask import Flask, render_template, request, session, redirect, flash
app=Flask(__name__)
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import math

with open('config.json','r') as c:
    params=json.load(c)['params']
current_dir=os.path.abspath(os.path.dirname(__file__))
print(current_dir)
app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///" + os.path.join(current_dir, "myblogdb.sqlite3")
app.secret_key='super-secret-key'
# if params['local_server']:
#     app.config["SQLALCHEMY_DATABASE_URI"]=params['local_uri']
# else:
#     app.config["SQLALCHEMY_DATABASE_URI"]=params['local_uri']
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
    tagline=db.Column(db.String, nullable=False)

@app.route("/")
def home():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts)/int(params['no_of_posts']))
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts = posts[(page-1)*int(params['no_of_posts']):(page-1)*int(params['no_of_posts'])+ int(params['no_of_posts'])]
    if page==1:
        prev = "#"
        next = "/?page="+ str(page+1)
    elif page==last:
        prev = "/?page="+ str(page-1)
        next = "#"
    else:
        prev = "/?page="+ str(page-1)
        next = "/?page="+ str(page+1)

    return render_template('index.html', params=params, posts=posts, prev=prev, next=next)

@app.route("/about")
def about():
    return render_template("about.html", params=params)

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
        flash("Thanks for submitting you message. We will get back to you","success")
    return render_template("contact.html", params=params)

@app.route('/admin_dashboard', methods=["Get","POST"])
def admin_dashboard():
    if "user" in session and session["user"]==params["admin_username"]:
        posts=Posts.query.all()
        return render_template("dashboard.html", params=params, posts=posts)
    if request.method=="POST":
        username=request.form.get("uname")
        password=request.form.get("password")
        if (username==params['admin_username'] and password ==params['admin_password']):
            session['user']=username
            posts=Posts.query.all()
            return render_template("dashboard.html", params=params, posts=posts)
    
    return render_template('admin_login.html', params=params)
@app.route('/edit/<string:post_id>', methods=["GET","POST"])
def edit_post(post_id):
    if "user" in session and session["user"]==params["admin_username"]:
        if request.method=="POST":
            title=request.form.get("title")
            tagline=request.form.get("tagline")
            slug=request.form.get("slug")
            content=request.form.get("content")
            img_file=request.form.get("img_file")
            date=datetime.now()
            posted_by=request.form.get("posted_by")
            if post_id=='0':
                post=Posts(title=title,tagline=tagline,slug=slug,content=content,img_file=img_file, post_id=post_id, date=date,posted_by=posted_by)
                db.session.add(post)
                db.session.commit()
            else:
                post=Posts.query.filter_by(post_id=post_id).first()
                post.title=title
                post.tagline=tagline
                post.slug=slug
                post.content=content
                post.img_file=img_file
                post.date=date
                post.posted_by=posted_by
                db.session.commit()
                return redirect('/edit/'+post_id)
        post=Posts.query.filter_by(post_id=post_id).first()
        return render_template("edit_post.html", params=params, post_id=post_id, post=post)
@app.route('/delete/<string:post_id>', methods=["GET","POST"])
def delete_post(post_id):    
    if "user" in session and session["user"]==params["admin_username"]:
        post=Posts.query.filter_by(post_id=post_id).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/admin_dashboard')
@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post=Posts.query.filter_by(slug=post_slug).first()
    return render_template("post.html", post=post, params=params)

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/admin_dashboard')

if __name__=="__main__":
    app.run(debug=True)