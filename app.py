from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from datetime import datetime
import os

# For Vercel serverless
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'hckvision_secret_key_2024')

# MongoDB connection
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb+srv://ExpenseTracker:Mahesh123@expensetracker.2u9oewp.mongodb.net/?appName=ExpenseTracker')
client = MongoClient(MONGO_URI)
db = client['hckvision_expenses']
expenses_collection = db['expenses']
director_investments_collection = db['director_investments']
director_profits_collection = db['director_profits']

# Static credentials
USERNAME = 'Bharath'
PASSWORD = 'Bharath1234'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == USERNAME and password == PASSWORD or username == 'Mahesh' and password == 'Mahesh1234':
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'error')
            return render_template('login.html', error=True)
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('dashboard.html', page='expenses')

@app.route('/expenses')
def expenses():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    expenses_list = list(expenses_collection.find().sort('date', 1))
    total = sum(expense['amount'] for expense in expenses_list)
    
    return render_template('expenses.html', expenses=expenses_list, total=total)

@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        amount = float(request.form.get('amount'))
        date = request.form.get('date')
        
        expense = {
            'title': title,
            'description': description,
            'amount': amount,
            'date': date,
            'added_by': session.get('username'),  # Store username
            'created_at': datetime.now()
        }
        
        expenses_collection.insert_one(expense)
        flash('Expense added successfully!', 'success')
        return redirect(url_for('expenses'))
    
    return render_template('add.html')

@app.route('/history')
def history():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    expenses_list = list(expenses_collection.find().sort('date', -1))
    total = sum(expense['amount'] for expense in expenses_list)
    
    return render_template('history.html', expenses=expenses_list, total=total)

@app.route('/director-investments')
def director_investments():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # Get all investments
    investments_list = list(director_investments_collection.find().sort('date', -1))
    total_investments = sum(inv['amount'] for inv in investments_list)
    
    # Get all profits
    profits_list = list(director_profits_collection.find().sort('date', -1))
    total_profits = sum(profit['amount'] for profit in profits_list)
    
    # Calculate profit
    profit = total_profits - total_investments
    
    # Calculate individual user totals
    users = ['Bharath', 'Mahesh']
    user_investments = {}
    user_profits = {}
    user_net = {}
    
    for user in users:
        user_inv_total = sum(inv['amount'] for inv in investments_list if inv['user'] == user)
        user_prof_total = sum(profit['amount'] for profit in profits_list if profit['user'] == user)
        user_investments[user] = user_inv_total
        user_profits[user] = user_prof_total
        user_net[user] = user_inv_total - user_prof_total
    
    return render_template('director_investments.html', 
                         investments=investments_list,
                         profits=profits_list,
                         total_investments=total_investments,
                         total_profits=total_profits,
                         profit=profit,
                         user_investments=user_investments,
                         user_profits=user_profits,
                         user_net=user_net)

@app.route('/add-director-investment', methods=['GET', 'POST'])
def add_director_investment():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        date = request.form.get('date')
        remarks = request.form.get('remarks')
        
        investment = {
            'user': session.get('username'),
            'amount': amount,
            'date': date,
            'remarks': remarks,
            'created_at': datetime.now()
        }
        
        director_investments_collection.insert_one(investment)
        flash('Director investment added successfully!', 'success')
        return redirect(url_for('director_investments'))
    
    return render_template('add_director_investment.html')

@app.route('/add-director-profit', methods=['GET', 'POST'])
def add_director_profit():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # Only Bharath can add profits
    if session.get('username') != 'Bharath':
        flash('Only Bharath can add director profits!', 'error')
        return redirect(url_for('director_investments'))
    
    if request.method == 'POST':
        user = request.form.get('user')
        amount = float(request.form.get('amount'))
        date = request.form.get('date')
        remarks = request.form.get('remarks')
        
        profit = {
            'user': user,
            'amount': amount,
            'date': date,
            'remarks': remarks,
            'added_by': session.get('username'),
            'created_at': datetime.now()
        }
        
        director_profits_collection.insert_one(profit)
        flash('Director profit added successfully!', 'success')
        return redirect(url_for('director_investments'))
    
    # Get list of users for dropdown
    users = ['Bharath', 'Mahesh']
    return render_template('add_director_profit.html', users=users)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

