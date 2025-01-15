from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import plotly.express as px
import pandas as pd
from config import Config
from extensions import db, login_manager
from models import User, Expense
from forms import RegisterForm, LoginForm, ExpenseForm
import os
import time

app = Flask(__name__)
app.config.from_object(Config)

# Ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)  # Use the model's method instead
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):  # Use the model's method
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
    
    # Create visualization data
    df = pd.DataFrame([(e.amount, e.category, e.date) for e in expenses], 
                     columns=['amount', 'category', 'date'])
    
    if not df.empty:
        fig = px.pie(df, values='amount', names='category', title='Expenses by Category')
        chart = fig.to_html(full_html=False)
    else:
        chart = None
        
    return render_template('dashboard.html', expenses=expenses, chart=chart)

@app.route('/add_expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    form = ExpenseForm()
    if form.validate_on_submit():
        expense = Expense(
            amount=form.amount.data,
            category=form.category.data,
            description=form.description.data,
            user_id=current_user.id
        )
        db.session.add(expense)
        db.session.commit()
        flash('Expense added successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_expense.html', form=form)

def init_db():
    db_path = os.path.join(app.instance_path, 'finance.db')
    
    # Only create database if it doesn't exist
    if not os.path.exists(db_path):
        try:
            with app.app_context():
                db.create_all()
                print(f"Database created successfully at {db_path}")
        except Exception as e:
            print(f"Error creating database: {e}")
            return False
    return True

if __name__ == '__main__':
    # Ensure instance directory exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Initialize database without removing existing one
    if init_db():
        app.run(debug=True)
    else:
        print("Database initialization failed. Please check permissions and try again.")
        exit(1)
