from flask import Flask, render_template, redirect, url_for, flash, request, send_file
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
import io
import csv
from werkzeug.utils import secure_filename

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
        df = pd.DataFrame([{
            'amount': e.amount,
            'category': e.category,
            'date': e.date,
            'description': e.description,
            'expense_type': e.expense_type,
            'honest_reason': e.honest_reason,
            'associated_person': e.associated_person
        } for e in expenses])
        
        # Calculate totals
        total_spent = sum(e.amount for e in expenses)
        essential_total = sum(e.amount for e in expenses if e.expense_type == 'essential')
        non_essential_total = sum(e.amount for e in expenses if e.expense_type == 'non-essential')
        
        if not df.empty:
            # Create expense type pie chart
            type_fig = px.pie(
                values=[essential_total, non_essential_total],
                names=['Essential', 'Non-Essential'],
                title='Essential vs Non-Essential Expenses',
                color_discrete_sequence=['#36a2eb', '#ff6384']
            )
            type_fig.update_traces(
                texttemplate="PGK %{value:.2f}<br>(%{percent})",
                hovertemplate="PGK %{value:.2f}<br>%{percent}"
            )
            type_chart = type_fig.to_html(full_html=False)
            
            # Create category bar chart
            cat_fig = px.bar(
                df.groupby(['category', 'expense_type'])['amount'].sum().reset_index(),
                x='category',
                y='amount',
                color='expense_type',
                title='Expenses by Category and Type',
                labels={'amount': 'Amount (PGK)', 'category': 'Category', 'expense_type': 'Type'},
                color_discrete_map={'essential': '#36a2eb', 'non-essential': '#ff6384'}
            )
            cat_fig.update_traces(
                hovertemplate="PGK %{y:.2f}<br>%{x}"
            )
            cat_fig.update_layout(
                yaxis_tickprefix='PGK ',
                yaxis_title='Amount (PGK)'
            )
            category_chart = cat_fig.to_html(full_html=False)
            
            # Create spending analysis text
            essential_percent = (essential_total/total_spent)*100 if total_spent > 0 else 0
            spending_analysis = f"Essential expenses: PGK {essential_total:.2f} ({essential_percent:.1f}%). "
            spending_analysis += f"Non-essential expenses: PGK {non_essential_total:.2f} ({100-essential_percent:.1f}%)"
        else:
            type_chart = None
            category_chart = None
            spending_analysis = f"No expenses recorded for {period_display.lower()}."
        
        return render_template('dashboard.html',
                             expenses=expenses,
                             chart=category_chart,
                             type_chart=type_chart,
                             total_spent=total_spent,
                             essential_total=essential_total,
                             non_essential_total=non_essential_total,
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
                    expense_type=form.expense_type.data,  # Add this line
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
            expense.associated_person = form.associated_person.data
            expense.expense_type = form.expense_type.data  # Add this line
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

    @app.route('/download_expenses')
    @login_required
    def download_expenses():
        # Get period from query parameters
        period = request.args.get('period', 'month')
        
        # Calculate date range (reuse logic from dashboard)
        today = datetime.now()
        if period == 'week':
            start_date = today - timedelta(days=today.weekday())
        elif period == 'month':
            start_date = today.replace(day=1)
        elif period == 'year':
            start_date = today.replace(month=1, day=1)
        else:  # 'all'
            start_date = None

        # Query expenses
        query = Expense.query.filter_by(user_id=current_user.id)
        if start_date:
            query = query.filter(Expense.date >= start_date)
        expenses = query.order_by(Expense.date.desc()).all()

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Date', 'Category', 'Type', 'Description', 'Honest Reason', 
                        'Associated Person', 'Amount'])
        
        # Write expenses
        for expense in expenses:
            writer.writerow([
                expense.date.strftime('%Y-%m-%d %H:%M'),
                expense.category,
                expense.expense_type,
                expense.description,
                expense.honest_reason,
                expense.associated_person,
                f"${expense.amount:.2f}"
            ])

        # Prepare the output
        output.seek(0)
        filename = f"expenses_{period}_{datetime.now().strftime('%Y%m%d')}.csv"
        
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )

    @app.route('/upload_expenses', methods=['POST'])
    @login_required
    def upload_expenses():
        if 'file' not in request.files:
            flash('No file selected', 'danger')
            return redirect(url_for('dashboard'))
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(url_for('dashboard'))

        if file and file.filename.endswith('.csv'):
            try:
                # Read CSV with more flexible column names
                df = pd.read_csv(file)
                # Standardize column names by removing spaces and converting to lowercase
                df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
                
                successful_imports = 0
                errors = []
                
                print("Columns found in CSV:", df.columns.tolist())  # Debug print
                
                for index, row in df.iterrows():
                    try:
                        # More flexible amount parsing
                        amount_str = str(row.get('amount', '')).replace('PGK', '').replace('$', '').strip()
                        amount = float(amount_str)
                        
                        # Get date with flexible column name
                        date_str = row.get('date', '') or row.get('datetime', '')
                        try:
                            date = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
                        except ValueError:
                            # Try alternative date formats
                            try:
                                date = datetime.strptime(date_str, '%Y-%m-%d')
                            except ValueError:
                                date = datetime.now()
                        
                        expense = Expense(
                            amount=amount,
                            category=row.get('category', 'Other'),
                            description=row.get('description', ''),
                            honest_reason=row.get('honest_reason', ''),
                            associated_person=row.get('associated_person', ''),
                            expense_type=row.get('type', 'non-essential').lower(),
                            date=date,
                            user_id=current_user.id
                        )
                        db.session.add(expense)
                        successful_imports += 1
                    except Exception as e:
                        errors.append(f"Error in row {index + 2}: {str(e)}")
                        continue

                if successful_imports > 0:
                    db.session.commit()
                    flash(f'Successfully imported {successful_imports} expenses!', 'success')
                else:
                    flash('No valid expenses found in the CSV file.', 'warning')
                
                if errors:
                    for error in errors[:5]:  # Show first 5 errors
                        flash(error, 'warning')
                    if len(errors) > 5:
                        flash(f'...and {len(errors) - 5} more errors', 'warning')
                
            except Exception as e:
                db.session.rollback()
                flash(f'Error processing CSV: {str(e)}', 'danger')
                print(f"CSV processing error: {str(e)}")  # Debug print
                
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
