from mongoengine.errors import NotUniqueError, ValidationError
from app import app
from flask import render_template, request, jsonify, make_response, redirect, url_for, g
from .models import User
import jwt
from datetime import datetime, timedelta
from app import app
import bcrypt
from functools import wraps

max_age = datetime.utcnow() + timedelta(minutes=30)

@app.before_request
def check_user():
    token = request.cookies.get('jwt')
    if not token:
        g.user = None
        pass
    else:
        data = jwt.decode(token, str(app.config['SECRET_KEY']))
        id = data['some']
        user = User.objects(id=id)[0]
        g.user = user

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('jwt')
        if not token:
            return redirect(url_for('login'))
        try:
            jwt.decode(token, str(app.config['SECRET_KEY']))
        except jwt.ExpiredSignatureError:
            return redirect(url_for('login'))
    
        return f(*args, **kwargs)

    return decorated

def create_token(id):
    token = jwt.encode({'some': id, 'exp': max_age},
                       key=str(app.config['SECRET_KEY']), algorithm='HS256')
    return token


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/smoothies', methods=['GET'])
@token_required
def smoothies():
    return render_template('smoothies.html')


@app.route('/login', methods=['GET'])
def login():
    if not g.user:
        return render_template('login.html')
    return redirect(url_for('home'))


@app.route('/login', methods=['POST'])
def login_post():
    data = request.json
    email, password = data['email'], data['password']

    user = User.objects(email=email)
    if user:
        if bcrypt.checkpw(password=password.encode("utf-8"), hashed_password=user[0].password.encode("utf-8")):
            id = str(user[0].id)
            token = create_token(id)
            resp = make_response(jsonify({'user': id}), 200)
            resp.set_cookie('jwt', token, expires=max_age, httponly=True)
            return resp
        else:
            pass
    else:
        pass
    return jsonify({'error': 'Invalid email or password'}), 400


@app.route('/signup', methods=['GET'])
def signup():
    if not g.user:
        return render_template('signup.html')
    return redirect(url_for('home'))


@app.route('/signup', methods=['POST'])
def signup_post():
    data = request.json
    email, password = data['email'], data['password']

    try:
        user = User(email=email, password=password)
        user.validate()
        user.hash_password()
        saved_object = user.save()
        id = str(saved_object.id)
        token = create_token(id)
        resp = make_response(jsonify({'user': id}), 201)
        resp.set_cookie('jwt', token, expires=max_age, httponly=True)
        return resp
    except NotUniqueError as _:
        return jsonify({"errors": {"email": "Email already exist", "password": ""}}), 400
    except ValidationError as err:
        err_dict = err.errors
        return jsonify({'errors': {
            'email': str(err_dict.setdefault('email', '')).split(':')[0],
            'password': str(err_dict.setdefault('password', '')).split(':')[0],
        }}), 400


@app.route('/logout', methods=['GET'])
def logout():
    if g.user:
        resp = make_response(redirect(url_for('home')))
        resp.set_cookie('jwt', '', max_age=0)
        return resp
    else:
        return redirect(url_for('home'))