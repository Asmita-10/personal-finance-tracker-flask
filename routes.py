from datetime import date
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import User, Expense
from forms import LoginForm, RegistrationForm, ExpenseForm


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash('Welcome back!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).limit(10).all()
    
    total_expenses = db.session.query(db.func.sum(Expense.amount)).filter_by(user_id=current_user.id).scalar() or 0
    expense_count = Expense.query.filter_by(user_id=current_user.id).count()
    
    category_totals = db.session.query(
        Expense.category,
        db.func.sum(Expense.amount)
    ).filter_by(user_id=current_user.id).group_by(Expense.category).order_by(db.func.sum(Expense.amount).desc()).limit(3).all()
    
    return render_template('dashboard.html', 
                           expenses=expenses, 
                           total_expenses=total_expenses,
                           expense_count=expense_count,
                           category_totals=category_totals)


@app.route('/expenses')
@login_required
def expenses():
    page = request.args.get('page', 1, type=int)
    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).paginate(page=page, per_page=10)
    return render_template('expenses.html', expenses=expenses)


@app.route('/expense/add', methods=['GET', 'POST'])
@login_required
def add_expense():
    form = ExpenseForm()
    if form.validate_on_submit():
        expense = Expense(
            amount=form.amount.data,
            category=form.category.data,
            date=form.date.data,
            description=form.description.data,
            user_id=current_user.id
        )
        db.session.add(expense)
        db.session.commit()
        flash('Expense added successfully!', 'success')
        return redirect(url_for('expenses'))
    
    if not form.date.data:
        form.date.data = date.today()
    
    return render_template('expense_form.html', form=form, title='Add Expense')


@app.route('/expense/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_expense(id):
    expense = Expense.query.get_or_404(id)
    
    if expense.user_id != current_user.id:
        flash('You do not have permission to edit this expense.', 'danger')
        return redirect(url_for('expenses'))
    
    form = ExpenseForm(obj=expense)
    if form.validate_on_submit():
        expense.amount = form.amount.data
        expense.category = form.category.data
        expense.date = form.date.data
        expense.description = form.description.data
        db.session.commit()
        flash('Expense updated successfully!', 'success')
        return redirect(url_for('expenses'))
    
    return render_template('expense_form.html', form=form, title='Edit Expense')


@app.route('/expense/delete/<int:id>', methods=['POST'])
@login_required
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    
    if expense.user_id != current_user.id:
        flash('You do not have permission to delete this expense.', 'danger')
        return redirect(url_for('expenses'))
    
    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted successfully!', 'success')
    return redirect(url_for('expenses'))
