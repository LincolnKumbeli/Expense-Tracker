from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, TextAreaField, SelectField, DateTimeLocalField, BooleanField
from wtforms.validators import DataRequired, Email, Length, Optional
from datetime import datetime

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ExpenseForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('Groceries', 'Groceries'),
        ('Transportation', 'Transportation'),
        ('Entertainment', 'Entertainment'),
        ('Utilities', 'Utilities'),
        ('Food', 'Food'),
        ('Shopping', 'Shopping'),
        ('Healthcare', 'Healthcare'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    expense_type = SelectField('Type', choices=[
        ('essential', 'Essential'),
        ('non-essential', 'Non-Essential')
    ], default='non-essential')
    description = TextAreaField('Description', validators=[Optional()])
    honest_reason = TextAreaField('Honest Reason for Spending', validators=[Optional()])
    associated_person = StringField('Associated Person', validators=[Length(max=256)])  # New field
    use_current_time = SelectField(
        'Timestamp',
        choices=[
            ('now', 'Use Current Time'),
            ('manual', 'Set Manual Time')
        ],
        default='now'
    )
    date = DateTimeLocalField(
        'Date and Time',
        format='%Y-%m-%dT%H:%M',
        validators=[Optional()],
        default=datetime.now
    )
    submit = SubmitField('Add Expense')
