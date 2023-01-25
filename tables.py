from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
##CONFIGURE Database Tables----------------------------------------------

class BlogPost(db.Model  , UserMixin):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    # relation b/w Users tables
    # Below, this refers to the user object of the current post
    author = relationship("Users" , back_populates="posts")
    author_id = db.Column(db.Integer , ForeignKey("users.id"), nullable=False)

    # relation with comment table
    comment = relationship("Comment" , back_populates="Parent_post")

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


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer , primary_key=True)
    comment =  db.Column(db.text , nullable=False)

    #relation with Users table
    user_id = db.Column(db.Integer , ForeignKey("users.id") , nullable=False)
    # this refers to the user object associated with the comment
    user =  relationship("Users" , back_populates="comments")

    # Relation with Blogpost table-----
    Parent_post = relationship("Blog_Post" , back_populate="comment")
    post_id = db.Column(db.Integer , ForeignKey("blog_posts.id"))