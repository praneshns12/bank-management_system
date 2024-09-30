import re

def validate_email(email):
    if not re.match(r'^[0-9a-zA-z]+@gmail.\w+$',email):
        raise ValueError("Invalid Email")
    return email
def validate_phone(phone):
    if not re.match(r'^[0-9]{10}$',phone):
        raise ValueError("Invalid Phone_number")
    return phone
def validate_account_number(account_number):
    account_number=str(account_number)
    if not re.match(r'^[0-9]{12,15}$',account_number):
        raise ValueError("Invalid Account Number")
    return account_number
def validate_account_type(account_type):
    if account_type.lower()  not in ['savings','current','salary']:
        raise ValueError("Give Valid Account Type")
    return account_type