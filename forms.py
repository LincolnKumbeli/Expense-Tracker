from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, TextAreaField, SelectField, DateTimeLocalField
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
        ('food', 'Food'),
        ('transport', 'Transport'),
        ('entertainment', 'Entertainment'),
        ('utilities', 'Utilities'),
        ('other', 'Other')
    ], validators=[DataRequired()])
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
