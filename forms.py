from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, DateField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange
from models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')


EXPENSE_CATEGORIES = [
    ('', 'All Categories'),
    ('food', 'Food & Dining'),
    ('transport', 'Transportation'),
    ('utilities', 'Utilities'),
    ('entertainment', 'Entertainment'),
    ('shopping', 'Shopping'),
    ('healthcare', 'Healthcare'),
    ('education', 'Education'),
    ('travel', 'Travel'),
    ('other', 'Other')
]


class ExpenseForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0.01, message='Amount must be greater than 0')])
    category = SelectField('Category', choices=EXPENSE_CATEGORIES[1:], validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    description = TextAreaField('Description (Optional)', validators=[Length(max=255)])
    submit = SubmitField('Save Expense')


class ExpenseFilterForm(FlaskForm):
    category = SelectField('Category', choices=EXPENSE_CATEGORIES)
    date_from = DateField('From Date', validators=[])
    date_to = DateField('To Date', validators=[])
    min_amount = FloatField('Min Amount', validators=[])
    max_amount = FloatField('Max Amount', validators=[])
    search = StringField('Search Description')
    submit = SubmitField('Filter')


class BudgetForm(FlaskForm):
    category = SelectField('Category', choices=EXPENSE_CATEGORIES[1:], validators=[DataRequired()])
    limit_amount = FloatField('Limit Amount ($)', validators=[DataRequired(), NumberRange(min=0.01, message='Limit must be greater than 0')])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Set Budget')


class ReminderForm(FlaskForm):
    bill_name = StringField('Bill Name', validators=[DataRequired(), Length(min=1, max=100)])
    due_date = DateField('Due Date', validators=[DataRequired()])
    amount = FloatField('Amount ($)', validators=[DataRequired(), NumberRange(min=0.01, message='Amount must be greater than 0')])
    submit = SubmitField('Save Reminder')


class GoalForm(FlaskForm):
    name = StringField('Goal Name', validators=[DataRequired(), Length(min=1, max=100)])
    target_amount = FloatField('Target Amount ($)', validators=[DataRequired(), NumberRange(min=0.01, message='Amount must be greater than 0')])
    current_amount = FloatField('Current Amount ($)', validators=[DataRequired(), NumberRange(min=0)])
    due_date = DateField('Target Date', validators=[DataRequired()])
    submit = SubmitField('Save Goal')
