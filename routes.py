from datetime import date
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import User, Expense, Budget, Reminder, Goal
from forms import LoginForm, RegistrationForm, ExpenseForm, ExpenseFilterForm, BudgetForm, ReminderForm, GoalForm
from sqlalchemy import func, extract


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


@app.route('/analytics')
@login_required
def analytics():
    import json
    from datetime import datetime, timedelta
    from calendar import monthrange
    
    category_data = db.session.query(
        Expense.category,
        db.func.sum(Expense.amount)
    ).filter_by(user_id=current_user.id).group_by(Expense.category).all()
    
    category_labels = [cat.capitalize() for cat, _ in category_data]
    category_amounts = [float(amt) for _, amt in category_data]
    
    today = datetime.now().date()
    six_months_ago = today - timedelta(days=180)
    
    monthly_data = db.session.query(
        db.func.extract('year', Expense.date).label('year'),
        db.func.extract('month', Expense.date).label('month'),
        db.func.sum(Expense.amount)
    ).filter(
        Expense.user_id == current_user.id,
        Expense.date >= six_months_ago
    ).group_by('year', 'month').order_by('year', 'month').all()
    
    monthly_labels = []
    monthly_amounts = []
    for year, month, amount in monthly_data:
        month_name = datetime(int(year), int(month), 1).strftime('%b %Y')
        monthly_labels.append(month_name)
        monthly_amounts.append(float(amount))
    
    total_expenses = db.session.query(db.func.sum(Expense.amount)).filter_by(user_id=current_user.id).scalar() or 0
    expense_count = Expense.query.filter_by(user_id=current_user.id).count()
    avg_expense = total_expenses / expense_count if expense_count > 0 else 0
    
    first_day_of_month = today.replace(day=1)
    this_month_total = db.session.query(db.func.sum(Expense.amount)).filter(
        Expense.user_id == current_user.id,
        Expense.date >= first_day_of_month
    ).scalar() or 0
    
    return render_template('analytics.html',
                           category_labels=json.dumps(category_labels),
                           category_amounts=json.dumps(category_amounts),
                           monthly_labels=json.dumps(monthly_labels),
                           monthly_amounts=json.dumps(monthly_amounts),
                           total_expenses=total_expenses,
                           expense_count=expense_count,
                           avg_expense=avg_expense,
                           this_month_total=this_month_total)


@app.route('/expenses')
@login_required
def expenses():
    page = request.args.get('page', 1, type=int)
    form = ExpenseFilterForm()
    
    query = Expense.query.filter_by(user_id=current_user.id)
    
    category = request.args.get('category', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    min_amount = request.args.get('min_amount', '')
    max_amount = request.args.get('max_amount', '')
    search = request.args.get('search', '')
    
    if category:
        query = query.filter(Expense.category == category)
        form.category.data = category
    
    if date_from:
        try:
            from datetime import datetime
            date_from_parsed = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(Expense.date >= date_from_parsed)
            form.date_from.data = date_from_parsed
        except ValueError:
            pass
    
    if date_to:
        try:
            from datetime import datetime
            date_to_parsed = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(Expense.date <= date_to_parsed)
            form.date_to.data = date_to_parsed
        except ValueError:
            pass
    
    if min_amount:
        try:
            min_val = float(min_amount)
            query = query.filter(Expense.amount >= min_val)
            form.min_amount.data = min_val
        except ValueError:
            pass
    
    if max_amount:
        try:
            max_val = float(max_amount)
            query = query.filter(Expense.amount <= max_val)
            form.max_amount.data = max_val
        except ValueError:
            pass
    
    if search:
        query = query.filter(Expense.description.ilike(f'%{search}%'))
        form.search.data = search
    
    expenses_paginated = query.order_by(Expense.date.desc()).paginate(page=page, per_page=10)
    
    has_filters = any([category, date_from, date_to, min_amount, max_amount, search])
    
    return render_template('expenses.html', expenses=expenses_paginated, form=form, has_filters=has_filters)


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


@app.route('/export/csv')
@login_required
def export_csv():
    import csv
    import io
    from flask import Response
    
    query = Expense.query.filter_by(user_id=current_user.id)
    
    category = request.args.get('category', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    min_amount = request.args.get('min_amount', '')
    max_amount = request.args.get('max_amount', '')
    search = request.args.get('search', '')
    
    if category:
        query = query.filter(Expense.category == category)
    
    if date_from:
        try:
            from datetime import datetime
            date_from_parsed = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(Expense.date >= date_from_parsed)
        except ValueError:
            pass
    
    if date_to:
        try:
            from datetime import datetime
            date_to_parsed = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(Expense.date <= date_to_parsed)
        except ValueError:
            pass
    
    if min_amount:
        try:
            min_val = float(min_amount)
            query = query.filter(Expense.amount >= min_val)
        except ValueError:
            pass
    
    if max_amount:
        try:
            max_val = float(max_amount)
            query = query.filter(Expense.amount <= max_val)
        except ValueError:
            pass
    
    if search:
        query = query.filter(Expense.description.ilike(f'%{search}%'))
    
    expenses = query.order_by(Expense.date.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Date', 'Category', 'Amount', 'Description'])
    
    for expense in expenses:
        writer.writerow([
            expense.date.strftime('%Y-%m-%d'),
            expense.category.capitalize(),
            f'{expense.amount:.2f}',
            expense.description or ''
        ])
    
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=expenses_{date.today().strftime("%Y%m%d")}.csv'}
    )


@app.route('/budgets', methods=['GET', 'POST'])
@login_required
def budgets():
    form = BudgetForm()
    
    if form.validate_on_submit():
        budget = Budget(
            category=form.category.data,
            limit_amount=form.limit_amount.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            user_id=current_user.id
        )
        db.session.add(budget)
        db.session.commit()
        flash('Budget created successfully!', 'success')
        return redirect(url_for('budgets'))
    
    user_budgets = Budget.query.filter_by(user_id=current_user.id).order_by(Budget.start_date.desc()).all()
    
    budgets_data = []
    
    for budget in user_budgets:
        spent_amount = db.session.query(func.sum(Expense.amount)).filter(
            Expense.user_id == current_user.id,
            Expense.category == budget.category,
            Expense.date >= budget.start_date,
            Expense.date <= budget.end_date
        ).scalar() or 0.0
        
        remaining = budget.limit_amount - spent_amount
        
        budgets_data.append({
            'budget': budget,
            'spent': spent_amount,
            'remaining': remaining,
            'progress_percent': min(100, (spent_amount / budget.limit_amount) * 100)
        })
    
    return render_template('budgets.html', budgets_data=budgets_data, form=form)


@app.route('/budget/delete/<int:id>', methods=['POST'])
@login_required
def delete_budget(id):
    budget = Budget.query.get_or_404(id)
    
    if budget.user_id != current_user.id:
        flash('You do not have permission to delete this budget.', 'danger')
        return redirect(url_for('budgets'))
    
    db.session.delete(budget)
    db.session.commit()
    flash('Budget deleted successfully!', 'success')
    return redirect(url_for('budgets'))


@app.route('/reminders', methods=['GET', 'POST'])
@login_required
def reminders():
    form = ReminderForm()
    
    if form.validate_on_submit():
        reminder = Reminder(
            bill_name=form.bill_name.data,
            due_date=form.due_date.data,
            amount=form.amount.data,
            user_id=current_user.id
        )
        db.session.add(reminder)
        db.session.commit()
        flash('Reminder added successfully!', 'success')
        return redirect(url_for('reminders'))
    
    user_reminders = Reminder.query.filter_by(user_id=current_user.id).order_by(Reminder.due_date.asc()).all()
    
    return render_template('reminders.html', reminders=user_reminders, form=form)


@app.route('/reminder/delete/<int:id>', methods=['POST'])
@login_required
def delete_reminder(id):
    reminder = Reminder.query.get_or_404(id)
    
    if reminder.user_id != current_user.id:
        flash('You do not have permission to delete this reminder.', 'danger')
        return redirect(url_for('reminders'))
    
    db.session.delete(reminder)
    db.session.commit()
    flash('Reminder deleted successfully!', 'success')
    return redirect(url_for('reminders'))


@app.route('/goals', methods=['GET', 'POST'])
@login_required
def goals():
    form = GoalForm()
    
    if form.validate_on_submit():
        goal = Goal(
            name=form.name.data,
            target_amount=form.target_amount.data,
            current_amount=form.current_amount.data,
            due_date=form.due_date.data,
            user_id=current_user.id
        )
        db.session.add(goal)
        db.session.commit()
        flash('Goal created successfully!', 'success')
        return redirect(url_for('goals'))
    
    user_goals = Goal.query.filter_by(user_id=current_user.id).order_by(Goal.due_date.asc()).all()
    
    goals_data = []
    for goal in user_goals:
        progress = (goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0
        goals_data.append({
            'goal': goal,
            'progress': min(100, progress),
            'remaining': max(0, goal.target_amount - goal.current_amount)
        })
    
    return render_template('goals.html', goals_data=goals_data, form=form)


@app.route('/goal/delete/<int:id>', methods=['POST'])
@login_required
def delete_goal(id):
    goal = Goal.query.get_or_404(id)
    
    if goal.user_id != current_user.id:
        flash('You do not have permission to delete this goal.', 'danger')
        return redirect(url_for('goals'))
    
    db.session.delete(goal)
    db.session.commit()
    flash('Goal deleted successfully!', 'success')
    return redirect(url_for('goals'))
