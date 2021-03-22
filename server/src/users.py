# Flask imports
from flask import Blueprint, request, redirect, url_for, render_template, flash
from flask_mail import Mail, Message

# Other installed modules imports
from werkzeug.local import LocalProxy
from functools import wraps

# Built-in modules imports
import os, json, sys, requests, uuid, string, random
from datetime import datetime, timedelta

# Local imports
from utils import db, render_response, mail




current_user = LocalProxy(lambda: _get_current_user())

_users = {}

def _get_current_user():
    global _users

    current_user = None
    session_key = request.cookies.get('__session')
    if session_key is not None:
        session = FirebaseSession.get_session(session_key=session_key)
        if session:
            if session.user_id in _users:
                return _users[session.user_id]
            current_user = User.get_user(email=session.user_id)
            if not current_user.authenticated:
                return None
            _users[session.user_id] = current_user
    return current_user


def login_user(user):
    session = FirebaseSession.get_session(user_id=user.email)
    if not session:
        session = FirebaseSession(user.email)
    return session


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


class User():
    def __init__(self, email, password, first_name, last_name, authenticated=False, admin=False, favorites=[], history=[], temp_password=None, temp_password_expire=None):
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.authenticated = authenticated
        self.admin = admin
        self.favorites = favorites
        self.history = history
        self.temp_password = temp_password
        self.temp_password_expire = temp_password_expire
        if temp_password_expire:
            self.temp_password_expire = temp_password_expire.replace(tzinfo=None)

    def save(self):
        user_doc = db.collection('user').where('email', '==', self.email).get()
        if user_doc:
            user_ref = db.collection('user').document(user_doc[0].id)
            user_ref.update({
                'email': self.email,
                'password': self.password,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'authenticated': self.authenticated,
                'admin': self.admin,
                'favorites': self.favorites,
                'history': self.history,
                'temp_password': self.temp_password,
                'temp_password_expire': self.temp_password_expire
                })
        else:
            db.collection('user').add({
                'email': self.email,
                'password': self.password,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'authenticated': self.authenticated,
                'admin': self.admin,
                'favorites': self.favorites,
                'history': self.history,
                'temp_password': self.temp_password,
                'temp_password_expire': self.temp_password_expire
                })

    @staticmethod
    def get_user(email=None):
        query = db.collection('user')
        if email:
            query = query.where('email', '==', email)
        query = query.get()
        if (len(query) == 0):
            return None
        return User(email=query[0].get('email'),
            password=query[0].get('password'),
            first_name=query[0].get('first_name'),
            last_name=query[0].get('last_name'),
            authenticated=query[0].get('authenticated'),
            admin=query[0].get('admin'),
            favorites=query[0].get('favorites'),
            history=query[0].get('history'),
            temp_password=query[0].get('temp_password'),
            temp_password_expire=query[0].get('temp_password_expire'))


class FirebaseSession():
    class Meta:
        collection_name = 'sessions'

    def __init__(self, user_id, session_key=None):
        self.user_id = user_id
        if session_key:
            self.session_key = session_key
        else:
            self.session_key = str(uuid.uuid4())
            db.collection('sessions').add({
                'session_key': self.session_key,
                'user_id': self.user_id
                })

    @staticmethod
    def get_session(session_key=None, user_id=None):
        query = db.collection('sessions')
        if session_key:
            query = query.where('session_key', '==', session_key)
        if user_id:
            query = query.where('user_id', '==', user_id)
        query = query.get()
        if (len(query) == 0):
            return None
        return FirebaseSession(user_id=query[0].get('user_id'), session_key=query[0].get('session_key'))

    @staticmethod
    def delete_session(session_key=None, user_id=None):
        query = db.collection('sessions')
        if session_key:
            query = query.where('session_key', '==', session_key)
        if user_id:
            query = query.where('user_id', '==', user_id)
        query = query.get()
        if (len(query) > 0):
            db.collection('sessions').document(query[0].id).delete()



user_blueprint = Blueprint('user_blueprint', __name__)


# Serves the login page
@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.get_user(email=request.form['email'])
        if user:
            # TODO: Add password hashing
            if user.password is not None and request.form['password'] == user.password:
                user.authenticated = True
                user.save()
                session = login_user(user)
                return render_response(redirect(url_for('index')), cookies={'__session': session.session_key})
        # TODO: Include message in login.html for failed login
        return render_response(render_template('login.html', failed_login=True))

    # Returns the login.html template with the given values
    return render_response(render_template('login.html'))


# Serves the sign up page
@user_blueprint.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        if User.get_user(email=request.form['email']):
            # TODO: Include message in login.html for user already exists
            return render_response(render_template('login.html', user_exists=True))
        # TODO: Add password hashing
        user = User(email=request.form['email'], password=request.form['password'], first_name=request.form['first-name'], last_name=request.form['last-name'], authenticated=True)
        user.save()
        session = login_user(user)
        return render_response(redirect(url_for('index')), cookies={'__session': session.session_key})

    # Returns the signup.html template with the given values
    return render_response(render_template('signup.html'))


@user_blueprint.route('/logout')
def logout():
    if current_user:
        current_user.authenticated = False
        current_user.save()
        FirebaseSession.delete_session(user_id=current_user.email)
    return render_response(redirect(url_for('index')), delete_cookies=['__session'])


@user_blueprint.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        user = User.get_user(email=request.form['email'])
        if user:
            # TODO: email temporary password to the user
            user.temp_password = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
            user.temp_password_expire = datetime.now() + timedelta(minutes=15)
            user.save()
            # msg = Message('Temporary Passoword', recipients=['brocksmith225@gmail.com'])
            # msg.html = '<p>Here is your temporary password:</p><h3>' + user.temp_password + '</h3>'
            # mail.send(msg)
            return render_response(render_template('reset_password_1.html', email=user.email))
        return render_response(render_template('forgot_password.html', no_account=True))

    # Returns the forgot_password.html template with the given values
    return render_response(render_template('forgot_password.html'))


@user_blueprint.route('/reset_password', methods=['POST'])
def reset_password():
    user = User.get_user(email=request.form['email'])
    if user:
        if user.temp_password and user.temp_password_expire > datetime.now(user.temp_password_expire.tzinfo) and user.temp_password == request.form['password']:
            user.password = None
            user.temp_password = None
            user.temp_password_expire = None
            user.save()
            return render_response(render_template('reset_password_2.html', email=user.email))
        if user.password is None:
            user.password = request.form['password']
            user.save()
            return render_response(redirect(url_for('user_blueprint.login')))
    return render_response(redirect(url_for('user_blueprint.login')))


# Serves the profile page
@user_blueprint.route('/profile')
@login_required
def profile():
    # Returns the profile.html template with the given values
    return render_response(render_template('profile.html', first_name=current_user.first_name))


# Serves the favorites page
@user_blueprint.route('/favorites')
@login_required
def favorites():
    favorites = []
    for favorite in current_user.favorites:
        story_ref = db.collection('stories').document(favorite['story'])
        story_doc = story_ref.get()
        page = story_doc.get('`page-nodes`.`' + favorite['page_id'] + '`')
        favorites.insert(0, (page['page-name'], favorite['story'] + "/" + favorite['page_id']))

    # Returns the favorites.html template with the given values
    return render_response(render_template('favorites.html', first_name=current_user.first_name, favorites=favorites))


@user_blueprint.route('/add_favorite', methods=['POST'])
def add_favorites():
    current_user.favorites.append({
        'page_id': request.form['page_id'],
        'story': request.form['story']
    })
    current_user.save()

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@user_blueprint.route('/remove_favorite', methods=['POST'])
def remove_favorite():
    page_id, story = request.form['page_id'], request.form['story']

    for favorite in current_user.favorites:
        if favorite['page_id'] == page_id and favorite['story'] == story:
            current_user.favorites.remove(favorite)
            break
    current_user.save()

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


# Serves the history page
@user_blueprint.route('/history')
@login_required
def history():
    history = current_user.history
    history_arr = []
    # [[(page_id, history)], []]

    # Tracking which story a page belongs to

    # Sort the history
    for i in range(len(history)):
        for j in range(i + 1, len(history)):
            if history[i]['last_updated'] < history[j]['last_updated']:
                history[i], history[j] = history[j], history[i]

    for hist in history:
        new_arr = []
        story_ref = db.collection('stories').document(hist['story'])
        story_doc = story_ref.get()
        for page_id in hist['pages']:
            page = story_doc.get('`page-nodes`.`' + page_id + '`')
            new_arr.insert(0, (page['page-name'], hist['story'] + "/" + page_id))
        history_arr.append(new_arr)

    # Returns the history.html template with the given values
    return render_response(render_template('history.html', history=history_arr))