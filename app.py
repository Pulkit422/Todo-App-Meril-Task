from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, bcrypt, login_manager, User, ToDo

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Registered successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('todo'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')


@app.route('/todo', methods=['GET', 'POST'])
@login_required
def todo():
    if request.method == 'POST':
        task = request.form['task']
        new_todo = ToDo(task=task, user_id=current_user.id)
        db.session.add(new_todo)
        db.session.commit()
        return redirect(url_for('todo'))
    todos = ToDo.query.filter_by(user_id=current_user.id).all()
    return render_template('todo.html', todos=todos)

@app.route('/update/<int:id>')
@login_required
def update(id):
    todo = ToDo.query.get(id)
    todo.status = "Done" if todo.status == "Pending" else "Pending"
    db.session.commit()
    return redirect(url_for('todo'))

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    todo = ToDo.query.get(id)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('todo'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
