from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, RadioField, SubmitField, TextAreaField, SelectField
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
    category = SelectField('Select Category')
    draft = SubmitField('Draft')
    publish = SubmitField('Publish')
class WritePost(FlaskForm):
    description = TextAreaField("Write here!", validators=[DataRequired()])

class Search(FlaskForm):
    search = StringField("Search", validators=[DataRequired()])
    submit = SubmitField("search")

class DraftForm(FlaskForm):
    view = SubmitField('View')

class ReplyForm(FlaskForm):
    description = TextAreaField('description', validators=[DataRequired()])
    submit = SubmitField('Submit')

class ReportForm(FlaskForm):
    reason = TextAreaField('Enter Reason', validators=[DataRequired()])
    submit = SubmitField('Submit')

class NoteForm(FlaskForm):
    note = TextAreaField('Write Note', validators=[DataRequired()])
    submit = SubmitField('Send')

class EditForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = EmailField("Email Address", validators=[DataRequired()])
    old_password = PasswordField("Old Password", validators=[DataRequired()])
    password = PasswordField("Password")
    confirm_password = PasswordField("Confirm Password", validators=[EqualTo('password', "Password is not same")])
    profile = FileField("choose image")
    update = SubmitField("Update")
    delete = SubmitField("Delete")

class OnlineStatusForm(FlaskForm):
    role =  SelectField("--Role--", choices=[('any','Any'),('reader','Reader'),('journalist','Journalist')])
    search = StringField("Account name")
    submit = SubmitField()

class CatgoryForm(FlaskForm):
    category = StringField("Enter Category Name", validators=[DataRequired()])
    submit  = SubmitField("ADD")

class ByCategoryForm(FlaskForm):
    submit = SubmitField()