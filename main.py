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
from datetime import datetime, timedelta
import calendar
from flask_migrate import Migrate

def create_app():
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
    migrate = Migrate(app, db)  # Initialize Flask-Migrate

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
        # Get selected period from query parameters
        period = request.args.get('period', 'month')
        
        # Calculate date range based on period
        today = datetime.now()
        if period == 'week':
            start_date = today - timedelta(days=today.weekday())
            period_display = f"Week of {start_date.strftime('%B %d, %Y')}"
        elif period == 'month':
            start_date = today.replace(day=1)
            period_display = today.strftime('%B %Y')
        elif period == 'year':
            start_date = today.replace(month=1, day=1)
            period_display = today.strftime('%Y')
        else:  # 'all'
            start_date = None
            period_display = "All Time"

        # Query expenses for the selected period
        query = Expense.query.filter_by(user_id=current_user.id)
        if start_date:
            query = query.filter(Expense.date >= start_date)
        expenses = query.order_by(Expense.date.desc()).all()
        
        # Create visualization data
        df = pd.DataFrame([(e.amount, e.category, e.date) for e in expenses], 
                         columns=['amount', 'category', 'date'])
        
        # Calculate total spent
        total_spent = sum(e.amount for e in expenses)
        
        if not df.empty:
            # Group by category and sum amounts
            category_sums = df.groupby('category')['amount'].sum()
            top_category = category_sums.idxmax()
            top_amount = category_sums.max()
            
            # Create bar chart
            fig = px.bar(
                df.groupby('category')['amount'].sum().reset_index(),
                x='category',
                y='amount',
                title='Expenses by Category',
                labels={'amount': 'Amount ($)', 'category': 'Category'},
                color='category'
            )
            fig.update_layout(showlegend=False)
            chart = fig.to_html(full_html=False)
            
            # Create spending analysis text
            spending_analysis = f"Your highest spending category is '{top_category}' at ${top_amount:.2f}. "
            spending_analysis += f"This represents {(top_amount/total_spent)*100:.1f}% of your total expenses."
        else:
            chart = None
            spending_analysis = f"No expenses recorded for {period_display.lower()}."
        
        return render_template('dashboard.html',
                             expenses=expenses,
                             chart=chart,
                             total_spent=total_spent,
                             spending_analysis=spending_analysis,
                             period=period,
                             period_display=period_display)

    @app.route('/add_expense', methods=['GET', 'POST'])
    @login_required
    def add_expense():
        form = ExpenseForm()
        if form.validate_on_submit():
            try:
                print(request.form)  # Print form data to debug
                expense = Expense(
                    amount=form.amount.data,
                    category=form.category.data,
                    description=form.description.data,
                    honest_reason=form.honest_reason.data,
                    associated_person=form.associated_person.data,  # New field
                    user_id=current_user.id,
                    date=datetime.now() if form.use_current_time.data == 'now' else form.date.data
                )
                db.session.add(expense)
                db.session.commit()
                flash('Expense added successfully!', 'success')
                return redirect(url_for('dashboard'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error adding expense: {str(e)}', 'danger')
        
        if form.errors:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{field}: {error}', 'danger')
        
        return render_template('add_expense.html', form=form)

    @app.route('/edit_expense/<int:id>', methods=['GET', 'POST'])
    @login_required
    def edit_expense(id):
        expense = Expense.query.get_or_404(id)
        if expense.user_id != current_user.id:
            flash('You cannot edit this expense.', 'danger')
            return redirect(url_for('dashboard'))
        
        form = ExpenseForm(obj=expense)
        if form.validate_on_submit():
            expense.amount = form.amount.data
            expense.category = form.category.data
            expense.description = form.description.data
            expense.honest_reason = form.honest_reason.data
            expense.associated_person = form.associated_person.data  # Ensure this is included
            db.session.commit()
            flash('Expense updated successfully!', 'success')
            return redirect(url_for('dashboard'))
        return render_template('edit_expense.html', form=form, expense=expense)

    @app.route('/delete_expense/<int:id>')
    @login_required
    def delete_expense(id):
        expense = Expense.query.get_or_404(id)
        if expense.user_id != current_user.id:
            flash('You cannot delete this expense.', 'danger')
            return redirect(url_for('dashboard'))
        
        db.session.delete(expense)
        db.session.commit()
        flash('Expense deleted successfully!', 'success')
        return redirect(url_for('dashboard'))

    return app

def init_db(app):
    db_path = os.path.join(app.instance_path, 'finance.db')
    
    # Check if the database exists
    if not os.path.exists(db_path):
        try:
            with app.app_context():
                db.create_all()
                print(f"Database created successfully at {db_path}")
                return True
        except Exception as e:
            print(f"Error creating database: {e}")
            return False
    else:
        print(f"Database already exists at {db_path}")
        return True

if __name__ == '__main__':
    app = create_app()
    
    # Ensure instance directory exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Initialize database without removing existing one
    if init_db(app):
        app.run(debug=True)
    else:
        print("Database initialization failed. Please check permissions and try again.")
        exit(1)
