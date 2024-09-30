from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import User, Account, Transaction
from validators import validate_email, validate_phone, validate_account_number, validate_account_type
import hashlib
import random
from datetime import datetime

main_blueprint = Blueprint('main', __name__)

@main_blueprint.route('/')
def main_menu():
    return render_template('main_menu.html')

@main_blueprint.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    email=''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.find_by_email(email)
        if user and user['password'] == hashlib.sha256(password.encode()).hexdigest() and 'admin' in user['roles']:
            session['user_id'] = user['id']
            session['roles'] = user['roles']
            return redirect(url_for('main.account_menu'))
        else:
            flash('Invalid credentials or not an admin')
    return render_template('login.html',email=email)

'''@main_blueprint.route('/create_account_login', methods=['GET', 'POST'])
def create_account_login():
    email = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = User.find_by_email(email)
        if users and users['password'] == hashlib.sha256(password.encode()).hexdigest() and 'customer' in users['roles']:
            return redirect(url_for('main.create_account'))
        else:
            flash('Invalid credentials or not a customer')
    return render_template('create_account_login.html', email=email)
'''


@main_blueprint.route('/user_details', methods=['GET'])
def user_details():
    users = User.user_details()
    return render_template('view_user_details.html', users=users)


@main_blueprint.route('/display_user_details', methods=['GET', 'POST'])
def display_user_details():
    users = None
    if request.method == 'POST':
        email = request.form['email'].lower()
        try:
            validate_email(email)
        except ValueError as e:
            flash(str(e))
            return render_template('view_user_by_email.html', email=email)

        user = User.find_by_email(email)
        if user:
            users = User.user_details_for_email(user['id'])
            flash('User searched successfully')
            return render_template('view_user_by_email.html', users=users)
        else:
            flash('User not found')

    return render_template('view_user_by_email.html', users=users)


'''
@main_blueprint.route('/delete_account_login', methods=['GET', 'POST'])
def delete_account_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.find_by_email(email)
        if user and user['password'] == hashlib.sha256(password.encode()).hexdigest() and 'customer' in user['roles']:
            return redirect(url_for('main.delete_account'))
        else:
            flash('Invalid credentials or not a customer')
    return render_template('delete_account_login.html')'''


'''@main_blueprint.route('/delete_login', methods=['GET', 'POST'])
def delete_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.find_by_email(email)
        if user and user['password'] == hashlib.sha256(password.encode()).hexdigest() and 'customer' in user['roles']:
            account_already_present=Account.find_by_email(user['id'])
            if not account_already_present:
                return redirect(url_for('main.delete_user'))
            else:
                flash("you cannot delete a user having Acccount ")
        else:
            flash('Invalid credentials or not a customer')
    return render_template('delete_login.html')'''

@main_blueprint.route('/user_login', methods=['GET', 'POST'])
def user_login():
    email = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.find_by_email(email)
        if user and user['password'] == hashlib.sha256(password.encode()).hexdigest() and 'customer' in user['roles']:
            session['user_id'] = user['id']
            session['roles'] = user['roles']
            return redirect(url_for('main.user_menu'))
        else:
            flash('Invalid credentials or not a customer')
    return render_template('login.html', email=email)


@main_blueprint.route('/account_menu')
def account_menu():
    if 'user_id' not in session or 'admin' not in session['roles']:
        return redirect(url_for('main.admin_login'))
    return render_template('account_menu.html')

@main_blueprint.route('/user_menu')
def user_menu():
    if 'user_id' not in session or 'customer' not in session['roles']:
        return redirect(url_for('main.user_login'))
    return render_template('user_menu.html')

@main_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email'].lower()
        roles = request.form['roles']
        phone = request.form['phone']
        
        try:
            validate_email(email)
            validate_phone(phone)
        except ValueError as e:
            flash(str(e))
            return render_template('register.html', username=username, email=email, roles=roles, phone=phone)
        
        user=User.find_by_email(email)
        if user['email'] :
            flash('Email already in use')
            return render_template('register.html', username=username, roles=roles, phone=phone)
        elif user['phone']:
            flash('Phone Number already in use')
            return render_template('register.html', username=username, roles=roles, email=email)
        
        user = User(username, password, email, roles, phone)
        user.save()
        flash('User registered successfully')
        return render_template('register.html', username=username, email=email, roles=roles, phone=phone)
    
    return render_template('register.html')



@main_blueprint.route('/delete_user', methods=['GET', 'POST'])
def delete_user():
    if request.method == 'POST':
        email = request.form['email'].lower()
        password = request.form['password']

        user = User.find_by_email(email)
        if not user or user['password'] != hashlib.sha256(password.encode()).hexdigest() or 'customer' not in user['roles']:
            flash('Invalid credentials or not a customer')
            return render_template('delete_user.html', email=email)

        account_already_present = Account.find_by_email(user['id'])
        if account_already_present:
            flash("You cannot delete a user having an account")
            return render_template('delete_user.html', email=email)

        try:
            validate_email(email)
        except ValueError as e:
            flash(str(e))
            return render_template('delete_user.html', email=email)

        if session['user_id'] != user['id'] and user['id'] != 1:
            User.delete(email)
            flash('User deleted successfully')
            return redirect(url_for('main.account_menu'))
        else:
            flash('User not found or User cannot delete their own information')
            return render_template('delete_user.html', email=email)

    return render_template('delete_user.html')

@main_blueprint.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        email = request.form['email']
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        if new_password == current_password:
            flash('New passwords should be unique')
            return redirect(url_for('main.change_password'))
        user = User.find_by_email(email)
        if user and hashlib.sha256(current_password.encode()).hexdigest() == user['password']:
            User.update_password(user['id'], new_password)
            flash('Password updated successfully')
            return redirect(url_for('main.main_menu'))
        else:
            flash('Current password is incorrect or user not found')
    
    return render_template('change_password.html')
@main_blueprint.route('/create_account', methods=['GET', 'POST'])
def create_account():
    email = ''
    account_holder = ''
    account_type = ''
    date_of_birth = ''
    phone = ''
    search = None  

    if request.method == 'POST':
        if 'step' not in request.form or request.form['step'] == 'login':
            email = request.form['email'].lower()
            password = request.form['password']

            user = User.find_by_email(email)
            if user and user['password'] == hashlib.sha256(password.encode()).hexdigest() and 'customer' in user['roles']:
                search = user['id']  
                return render_template('create_account.html', step='create', email=email, search=search)
            else:
                flash('Invalid credentials or not a customer')
                return render_template('create_account.html', step='login', email=email)
        
        elif request.form['step'] == 'create':
            account_holder = request.form['account_holder']
            account_type = request.form['account_type']
            date_of_birth = request.form['date_of_birth']
            phone = request.form['phone']
            search = request.form['search'] 
            try:
                search = int(search)
            except ValueError:
                flash("Invalid user ID provided")
                return render_template('create_account.html', step='login', email=email)

            user = User.find_by_id(search)
            if user:
                account_number = generate_account_number()
                try:
                    validate_account_number(account_number)
                    validate_account_type(account_type)
                except ValueError as e:
                    flash(str(e))
                    return render_template('create_account.html', step='create', email=email, account_holder=account_holder, account_type=account_type, date_of_birth=date_of_birth, phone=phone)

                account = Account.find_by_account_numbers(account_number)
                account1 = Account.numbers(phone)
                if account1:
                    flash("Phone Number Already Used")
                    return render_template('create_account.html', step='create', email=email, account_holder=account_holder, account_type=account_type, date_of_birth=date_of_birth, phone=phone)
                if account:
                    account_number = generate_account_number()

                creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if date_of_birth > creation_date:
                    flash("Invalid DOB")
                    return render_template('create_account.html', step='create', email=email, account_holder=account_holder, account_type=account_type, date_of_birth=date_of_birth, phone=phone)

                account = Account(account_number, account_holder, account_type, 0.0, user['id'], date_of_birth, creation_date, None, phone, user['id'])
                account.save()
                flash('Account created successfully')
            else:
                flash('No user exists')
                return render_template('create_account.html', step='create', email=email, account_holder=account_holder, account_type=account_type, date_of_birth=date_of_birth, phone=phone)

    return render_template('create_account.html', step='login', email=email, account_holder=account_holder, account_type=account_type, date_of_birth=date_of_birth, phone=phone)


@main_blueprint.route('/delete_account', methods=['GET', 'POST'])
def delete_account():
    if request.method == 'POST':
        email = request.form['email'].lower()
        password = request.form['password']
        account_number = request.form['account_number']

        user = User.find_by_email(email)
        if not user or user['password'] != hashlib.sha256(password.encode()).hexdigest() or 'customer' not in user['roles']:
            flash('Invalid credentials or not a customer')
            return render_template('delete_account.html', email=email, account_number=account_number)

        try:
            validate_email(email)
        except ValueError as e:
            flash(str(e))
            return render_template('delete_account.html', email=email, account_number=account_number)

        account = Account.find_by_account_number(account_number)
        if account:
            Account.delete(account_number)
            flash('Account deleted successfully')
            return redirect(url_for('main.account_menu'))
        else:
            flash('Account not found')
            return render_template('delete_account.html', email=email, account_number=account_number)

    return render_template('delete_account.html')

@main_blueprint.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        password = request.form['password']
        user_id = session.get('user_id')
        account = Account.numberss(user_id)
        if not account:
            flash("You have No Account")
            return render_template('withdraw.html')
        user = User.find_by_id(user_id)
        if account.customer_id== user_id:
            if user and user['password'] == hashlib.sha256(password.encode()).hexdigest() and 'customer' in user['roles']:
                try:
                    account.withdraw(amount, account.account_number)
                    transaction = Transaction(account.account_number, 'Withdraw', amount, account.account_number)
                    transaction.save()
                    flash('Withdrwn successfully')
                except ValueError as e:
                    flash(str(e))
            else:
                flash("Enter correct Password")
            return redirect (url_for('main.withdraw'))
        else:
            flash('Account not found or unauthorized access')
    
    return render_template('withdraw.html')


@main_blueprint.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        user_id = session.get('user_id')
        if not Account.numberss(user_id):
            flash("You have No Account")
            return render_template('deposit.html')
        account = Account.numberss(user_id)
        if account.customer_id== user_id:
            try:
                account.deposit(amount, account.account_number)
                transaction = Transaction(account.account_number, 'Deposit', amount, account.account_number)
                transaction.save()
                flash('Deposited successfully')
            except ValueError as e:
                flash(str(e))
        else:
            flash('Account not found or unauthorized access')
    
    return render_template('deposit.html')


@main_blueprint.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if request.method == 'POST':
        phone = request.form['phone']
        amount = float(request.form['amount'])
        password = request.form['password']
        sender_account = Account.find_by_email(session['user_id'])
        receiver_account = Account.numbers(phone)
        user = User.find_by_id(session['user_id'])
        if not Account.numberss(session['user_id']):
            flash("You have No Account")
            return render_template('transfer.html')
        if sender_account and receiver_account and sender_account.created_by == session['user_id']:
            if receiver_account.account_number==sender_account.account_number:
                flash("sender and reciever cannot be equal")
                return render_template('transfer.html')
            if not user and not user['password'] == hashlib.sha256(password.encode()).hexdigest() and 'customer' in user['roles']:
                return redirect (url_for('main.transfer'))

            try:
                receiver_account.deposit(amount,receiver_account.account_number)
                sender_account.withdraw(amount,sender_account.account_number)
                sender_transaction = Transaction(sender_account.account_number, 'Transfer', -amount, receiver_account.account_number)
                sender_transaction.save()
                receiver_transaction = Transaction(receiver_account.account_number, 'Transfer', amount, sender_account.account_number)
                receiver_transaction.save()
                flash('Transfer successful')
                return redirect(url_for('main.user_menu'))
            except ValueError as e:
                flash(str(e))
        else:
            flash('Account not found or unauthorized access')
    
    return render_template('transfer.html')

@main_blueprint.route('/check_balance', methods=['GET', 'POST'])
def check_balance():
    user_id = session.get('user_id')
    account = Account.numberss(user_id)
    if not account:
            flash("You have No Account")
            return render_template('check_balance.html')
    if account.customer_id== user_id:
            return render_template('check_balance.html', account=account)
    else:
        flash('Account not found or unauthorized access')
    return render_template('check_balance.html')

@main_blueprint.route('/view_account_details', methods=['GET', 'POST'])
def view_account_details():
    user_id = session.get('user_id')
    account,creator_name = Account.number(user_id)
    if not account:
        flash("You have No Account")
        return render_template('view_account_details.html')
    if account.customer_id== user_id:
        transactions = Transaction.find_by_account_number(account.account_number)
        return render_template('view_account_details.html', account=account, transactions=transactions,creator_name=creator_name)
    else:
        flash('Unauthorized access to the account')

    return render_template('view_account_details.html')


@main_blueprint.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('roles', None)
    flash('Logged out successfully')
    return redirect(url_for('main.main_menu'))

def generate_account_number():
    account_number = random.randint(1000000000000,999999999999999)
    return account_number
@main_blueprint.route('/view_account_transactions/<int:account_number>', methods=['GET'])
def view_account_transactions(account_number):
    account = Account.find_by_account_numbers(account_number)
    transactions = Transaction.find_by_account_number(account_number)
    return render_template('account_transactions.html', account=account, transactions=transactions)
