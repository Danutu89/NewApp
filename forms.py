from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, SelectField, SubmitField, TextField, TextAreaField
from wtforms.validators import Length, Email, EqualTo 

class RegisterForm(FlaskForm):

    username = TextField(
        'Username_Register',
        validators = [
            Length(min=5,max=15)
        ],
        render_kw = {
            "class":"form-control",
            "required":"true",
            "placeholder":"Username"
        }
    )
    email = TextField(
        'Email_Register',
        validators = [
            Email(message=None),
            Length(min=6,max=30)
        ],
        render_kw = {
            "class":"form-control",
            "required":"true",
            "placeholder":"Email"
        }
    )
    realname = TextField(
        'RealName_Register',
        validators = [
            Email(message=None),
            Length(min=6,max=30)
        ],
        render_kw = {
            "class":"form-control",
            "required":"true",
            "placeholder":"Real Name"
        }
    )
    github = TextField(
        'Github_Register',
        validators = [
            Email(message=None),
            Length(min=6,max=30)
        ],
        render_kw = {
            "class":"form-control",
            "required":"true",
            "placeholder":"Github Name"
        }
    )
    password = PasswordField(
        'Password_Register',
        validators = [
            Length(min=6,max=25)
        ],
        render_kw = {
            "class":"form-control",
            "required":"true",
            "placeholder":"Password"
        }
    )
    confirm_password = PasswordField(
        'Confirm_Password_Register',
        validators = [
            EqualTo('Password', message='Passwords must match')
        ],
        render_kw = {
            "class":"form-control",
            "required":"true",
            "placeholder":"Confirm Password"
        }
    )
    submit = SubmitField(
        'Register',
        render_kw = {
            "class":"btn btn-primary",
        }
    )

class LoginForm(FlaskForm):
    username = TextField(
        'Username_Login',
        render_kw = {
            "class":"form-control",
            "required":"true",
            "placeholder":"Username/Email"
        }
    )
    password = PasswordField(
        'Password_Login',
        render_kw = {
            "class":"form-control",
            "required":"true",
            "placeholder":"Password"
        }
    )
    submit = SubmitField(
        'Login',
        render_kw = {
            "class":"btn btn-primary"
        }
    )

class ModifyProfileForm(FlaskForm):

    username = TextField(
        'Username_ModifyProfile',
        validators = [
            Length(min=5,max=15)
        ],
        render_kw = {
            "class":"form-control",
            "placeholder":"Username"
        }
    )
    email = TextField(
        'Email_ModifyProfile',
        validators = [
            Email(message=None),
            Length(min=6,max=30)
        ],
        render_kw = {
            "class":"form-control",
            "placeholder":"Email"
        }
    )
    realname = TextField(
        'RealName_ModifyProfile',
        validators = [
            Length(min=6,max=30)
        ],
        render_kw = {
            "class":"form-control",
            "placeholder":"Real Name"
        }
    )
    bio = TextField(
        'Bio_ModifyProfile',
        render_kw = {
            "class":"form-control",
            "placeholder":"Bio"
        }
    )
    avatar = TextField(
        'Avatar_ModifyProfile',
        render_kw = {
            "class":"form-control",
            "placeholder":"Avatar Link"
        }
    )
    genre = SelectField(
        choices=[('Male','Male'),('Female','Female')],
        render_kw = {
            "class":"custom-select custom-select-sm"
        }
    )
    submit = SubmitField(
        'Modify Profile',
        render_kw = {
            "class":"btn btn-primary",
        }
    )

class SearchForm(FlaskForm):
    search = TextField(
        'Arguments_Search',
        validators = [
            Length(max=20)
        ],
        render_kw = {
            "class":"form-control form-control-sm",
            "placeholder":"Search Posts"
        }
    )
    submit = SubmitField(
        'Search',
        render_kw = {
            "class":"btn btn-search my-2 my-sm-0",
        }
    )

class NewQuestionForm(FlaskForm):
    title = TextField(
        'NewQuestionForm_Title',
        render_kw = {
            "class":"form-control form-control-sm",
            "placeholder":"Title",
            "style":"margin-bottom: 5px;",
            "required":"true"
        }
    )
    text = TextAreaField(
        'NewQuestionForm_Text',
        render_kw = {
            "class":"form-control form-control-sm",
            "placeholder":"Text",
            "rows":5,
            "style":"margin-bottom: 5px;",
            "id":"summernote",
            "required":"true"
        }
    )
    tag = TextField(
        'NewQuestionForm_Tags',
        render_kw = {
            "class":"form-control form-control-sm",
            "placeholder":"Tags",
            "style":"margin-top: 5px;"
        }
    )
    submit = SubmitField(
        'Ask',
        render_kw = {
            "class":"btn btn-primary btn-sm",
            "style":"float:right;"
        }
    )

class ReplyForm(FlaskForm):
    reply = TextAreaField(
        'ReplyForm_Text',
        render_kw = {
            "class":"form-control form-control-sm",
            "placeholder":"Text",
            "rows":5,
            "style":"margin-bottom: 5px;",
            "id":"summernote",
            "required":"true"
        }
    )
    submit = SubmitField(
        'Reply',
        render_kw = {
            "class":"btn btn-primary btn-sm",
            "style":"float:right;"
        }
    )