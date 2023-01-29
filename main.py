from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import *
from flask_gravatar import Gravatar
from functools import wraps
from dotenv import load_dotenv
import os
import psycopg2


#loading dotenv....
try:
    load_dotenv(".env")
except:
    pass


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("app_token")
ckeditor = CKEditor(app)
Bootstrap(app)


##CONNECT TO DB-------------------------------------------------------
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('Database_url' , 'sqlite:///blog.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


#app Login Manager config. ------------------------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def user_loader(user_id):
    return Users.query.get(user_id)

#gravatar intialization for comment
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)


# admin only decorator ----------------------
def admin_only(function):
    @wraps(function)
    def wrap(*args , **kwargs):
        if current_user.get_id() == '1':
           return function(*args , **kwargs)
        else:
           return abort(403)


    return wrap


# identifying admin func.------------------------
def is_admin():
    if current_user.get_id() == '1':
        return True
    else :
        return False




##CONFIGURE Database Tables----------------------------------------------
class BlogPost(db.Model  , UserMixin):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    #Child relation with Users tables
    author_id = db.Column(db.Integer , ForeignKey("users.id"), nullable=False)
    # Below code, refers to the user object of the current post
    author = relationship("Users" , back_populates="posts")

    #Parent relationship with comment table
    comment = relationship("Comment" , back_populates="parent_post")

class Users(db.Model , UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer , primary_key=True)
    email = db.Column(db.String(250) , unique=True , nullable=False)
    name =  db.Column(db.String(250) , nullable=False)
    password = db.Column(db.String(250) , nullable=False)

    #This will act like a List of BlogPost objects attached to each User.
    posts = relationship("BlogPost" , back_populates="author")
    #This will act like a List of comment objects attached to each User.
    comments = relationship("Comment" , back_populates="user")


class Comment(db.Model , UserMixin):
    __tablename__ = "comments"
    id = db.Column(db.Integer , primary_key=True)
    comment =  db.Column(db.Text , nullable=False)

    #Child relationship with Users table----------------------
    user_id = db.Column(db.Integer , ForeignKey("users.id") , nullable=False)
    # this refers to the user object associated with the comment
    user =  relationship("Users" , back_populates="comments")

    #Child Relationship with Blogposts table---------------
    parent_post = relationship("BlogPost" , back_populates="comment")
    post_id = db.Column(db.Integer , ForeignKey("blog_posts.id"))



with app.app_context():
    db.create_all()





#-------------------------All app routes----------------------------------------



#home route---------------
@app.route('/')
def get_all_posts():
    try :
        all_posts = db.session.execute(db.select(BlogPost).order_by(BlogPost.id)).scalars()
    except:
        all_posts = ""
    return render_template("index.html", admin=is_admin(), all_posts=all_posts)


#-----------------User register route-----------------------------------!

@app.route('/register' , methods=["GET" , "POST"])
def register():
    form = Register_form()
    if form.validate_on_submit():

        name = form.name.data
        email = form.email.data
        password = form.password.data

        #checking if the user alredy exists in our database
        if db.session.execute(db.select(Users).filter_by(email=email)).first():
            flash(
                "Account associated with this email already exists , Login in your account",
                "error")
            return redirect(url_for("login"))

        password = generate_password_hash(      #Generating hashed password
            password= password,
            salt_length= 10
        )

        new_user = Users(
            name = name,
            email = email,
            password = password
        )
        db.session.add(new_user)
        db.session.commit()                 #Adding user in the database

        login_user(new_user)

        return redirect(url_for("get_all_posts"))

    return render_template("register.html" , form=form)


#-------------------------Login route-----------------------------------

@app.route('/login' , methods=["GET", "POST"])
def login():

    form = Login_form()

    if form.validate_on_submit():

        email = form.email.data
        entered_password = form.password.data

        try:
            user_account = db.session.execute(db.select(Users).filter_by(email=email)).scalar_one()
        except:
            flash("No Account associated with this email, try again or Register" , "error")
            return redirect(url_for("login"))

        actual_password = user_account.password

        if check_password_hash(actual_password , entered_password):
            login_user(user_account)
            return redirect(url_for("get_all_posts" ))
        else :
            flash("incorrect password" , "error")
            return redirect(url_for("login"))


    return render_template("login.html" , form=form)


#logout route-------------------------------

@app.route('/logout')
@login_required
def logout():
    if  current_user.is_authenticated == False :
        return redirect(url_for("login"))

    logout_user()
    return redirect(url_for('get_all_posts'))


#routes which don't need login--------------------------------------------
#Post route
@app.route("/post/<int:post_id>" , methods=["GET" , "POST"])
def show_post(post_id):
    form = Comments_form()      #comment form object
    requested_post = BlogPost.query.get(post_id)


    if form.validate_on_submit():            #users can add comments
      if current_user.is_authenticated :     #only if they are logged in
        new_comment = Comment(
            comment = form.comment.data,
            user = current_user,
            parent_post = requested_post
        )
        db.session.add(new_comment)
        db.session.commit()

        return redirect(url_for("show_post" ,post_id=post_id))

      else:
        flash("pls login to make comments on posts" , "error")
        return redirect(url_for("login"))   #asking to login to add comments


    return render_template("post.html", admin=is_admin(), form=form,  post=requested_post)


#-----------About , contact pages--------------------------------
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


# --------------------------Admin only routes-------------------------------------------------
#Add new post route--------

@app.route("/new-post" , methods=["GET", "POST"])
@admin_only
@login_required
def add_new_post():

    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html",admin=is_admin(), form=form)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
@login_required
def edit_post(post_id):

    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = edit_form.author.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id ))

    return render_template("make-post.html", form=edit_form)


#Delete post route-------------------------
@app.route("/delete/<int:post_id>")
@admin_only
@login_required
def delete_post(post_id):

    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))



#-------------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
