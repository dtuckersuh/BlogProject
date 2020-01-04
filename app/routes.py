from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from werkzeug.urls import url_parse
from datetime import datetime


@app.route('/')
@app.route('/index')
@login_required
# Homepage view
def index():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'What a beautiful Christmas!'
        },
        {
            'author': {'username': "Christie"},
            'body': 'Why, thank you John!'
        },
        {
            'author': {'username': 'John'},
            'body': "I wasn't talking about you Christie. Not everything is about you."
        },
        {
            'author': {'username': 'Christie'},
            'body': 'Well John, I see somebody is still bitter about the divorce.'
        },
        {
            'author': {'username': 'John'},
            'body': 'Well Christie, I see somebody still is not able to read.'
        },
        {
            'author': {'username': 'Christie'},
            'body': 'Jesus John, when will you ever grow up. You child.'
        },
        {
            'author': {'username': 'John'},
            'body': "At least I can read Christie."
        }
    ]
    return render_template('index.html', title='Home', posts=posts)


# Login view
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:   # User is remembered
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        # Username or password not valid
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        # request.args exposes contents of query string in dictionary format
        next_page = request.args.get('next') 
        # if url doesn't have next arg or next arg is full URL w/ domain name, redirect to index
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign in', form=form)

# Logout view
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# Register view
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:   # User is remembered
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, ' + user.username + ', you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

# User Profile Page
@app.route('/user/<username>')  # Dynamic component <username>
@login_required                 # Only accessible to logged in users
def user(username):
    # Load user from db using query by username
    user = User.query.filter_by(username=username).first_or_404()   # 404 if no result
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)     # Refer to user.html in templates

# Record time of last visit
@app.before_request     # before_request registers function to be executed right before view
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

# Edit profile view function
@app.route('/edit/profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():   # copy data from form into user object
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()         # write object into db
        flash('Your changes have been saved')
        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET':   # Provide initial version of the form template
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

