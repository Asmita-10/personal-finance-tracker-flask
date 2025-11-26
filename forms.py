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


class ExpenseForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0.01, message='Amount must be greater than 0')])
    category = SelectField('Category', choices=[
        ('food', 'Food & Dining'),
        ('transport', 'Transportation'),
        ('utilities', 'Utilities'),
        ('entertainment', 'Entertainment'),
        ('shopping', 'Shopping'),
        ('healthcare', 'Healthcare'),
        ('education', 'Education'),
        ('travel', 'Travel'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    description = TextAreaField('Description (Optional)', validators=[Length(max=255)])
    submit = SubmitField('Save Expense')
