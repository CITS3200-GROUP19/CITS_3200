from flask import render_template, flash
from app import app
from app.forms import LoginForm, AdminForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User

# can add @login_required for things that require login

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return render_template("home.html")
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return render_template("login.html")
        login_user(user, remember=form.remember_me.data)
        return render_template("home.html")
    return render_template("login.html", form=form)

@app.route('/logout')
def logout():
    logout_user()
    return render_template("home.html")

@app.route("/about")
def about():
	return render_template("about.html")

@app.route("/admin")
def admin():
	form = AdminForm()
	return render_template("admin.html", form=form)

@app.route("/user")
def user():
	return render_template("userPage.html")

@app.route("/query")
def query():
	return render_template("query.html")

@app.route("/user_manual")
def user_manual():
	return render_template("userManual.html")
