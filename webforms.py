from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, RadioField, SubmitField, TextAreaField
from flask_wtf.file import FileRequired, FileField
from wtforms.validators import DataRequired, EqualTo

class SignUpForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = EmailField("Email Address", validators=[DataRequired()])
    role = RadioField("role", choices=[('reader', 'reader'), ('journalist', 'journalist')], validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[EqualTo('password', "Password is not same")])
    profile = FileField("choose image", validators=[FileRequired()])
    submit = SubmitField("Sign Up")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign In")

class WriteNewsForm(FlaskForm):
    image = FileField("Choose Image", validators=[FileRequired()])
    title = StringField("Write Title of your News", validators=[DataRequired()])
    description = TextAreaField("Write your News descripton", validators=[DataRequired()])

class WritePost(FlaskForm):
    description = TextAreaField("Write here!", validators=[DataRequired()])

class Search(FlaskForm):
    search = StringField("Search", validators=[DataRequired()])
    submit = SubmitField("search")