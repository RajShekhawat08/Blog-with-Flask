from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField, EmailField
from wtforms.validators import DataRequired, URL , Email
from flask_ckeditor import CKEditorField

##WTForms-------------------------

class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


class Register_form(FlaskForm):
    name = StringField("Name" , validators=[DataRequired()])
    email = EmailField("Email" , validators=[DataRequired() , Email()])
    password = PasswordField("Password" , validators=[DataRequired()])
    submit = SubmitField("Sign Up")


class Login_form(FlaskForm):
    email = EmailField("Email" , validators=[DataRequired(), Email()])
    password = PasswordField("Password" , validators=[DataRequired()])
    submit = SubmitField("Let me in")


class Comments_form(FlaskForm):
    comment = TextAreaField("Comment")
    submit = SubmitField("comment")