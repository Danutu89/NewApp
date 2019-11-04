from forms import LoginForm, RegisterForm, ResetPasswordForm
from flask import request
from flask import render_template

def include_user(fn):
    login = LoginForm(request.form)
    register = RegisterForm(request.form)
    reset = ResetPasswordForm(request.form)
    template_name = fn()
    var1, var2, var3 = generate_sidebar_data()
    def wrapped():
        return render_template(template_name,reset=reset,login=login,register=register)
    return wrapped