from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from forms import LoginForm, RegisterForm
from book_recommender import find_k_similar_books, book_lookup, get_top_books
from flask import Flask, render_template, request, jsonify, Response
import json
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'IamTheSecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    filtered_books = get_top_books(n=200)

    return render_template('dashboard.html', books=filtered_books)

@app.route('/search_book', methods=['GET'])
@login_required
def search_book():
    search_string = request.args.get('search_field')

    filtered_books = book_lookup(search_string, n=32)

    return render_template('dashboard.html', books=filtered_books)

@app.route('/book_recommendations/<id_goodreads>')
@login_required
def book_recommendations(id_goodreads):
    recommended_books = find_k_similar_books(goodreads_book_id=id_goodreads, n=4)

    return render_template('dashboard.html', books=recommended_books)

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/', methods=['GET', 'POST'])
def index():
    login_form = LoginForm()
    register_form = RegisterForm()

    if 'submit_login' in request.form and login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.username.data).first()
        if user and user.password == login_form.password.data:
            login_user(user)
            return redirect(url_for('dashboard'))

    if 'submit_register' in request.form and register_form.validate_on_submit():
        user = User.query.filter_by(username=register_form.username.data).first()
        if user:
            flash('Username already exists', 'danger')
        else:
            new_user = User(username=register_form.username.data, password=register_form.password.data)
            db.create_all()
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('dashboard'))

    return render_template('index.html', login_form=login_form, register_form=register_form)

if __name__ == '__main__':
    app.run(debug=True)
