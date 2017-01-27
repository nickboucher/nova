#!/usr/bin/env python3
#
# installation.py
# Nicholas Boucher 2017
#
# Contains an installation script that creates and configures the 
# SQLlite database. Should be invoked via the command line (i.e.
# `python3 installation.py`).
#

from sys import exit
from os import path, rename
from datetime import datetime
from getpass import getpass
from database_models import db, Config, Grants_Week
from helpers import create_user
from application import app

def install_wizard():
    """ Runs a command-line series of prompt to gather proper paramaters and then
        creates the database """
    # Check if SQLlite database file already exists
    if path.isfile('database.db'):
        overwrite = input("The database file already exists. Would you like to discard it and start over?\nWARNING: This will delete the entire grant archive.\n(y/n): ")
        if overwrite == 'n':
            # Exit if overwriting denied
            print("No chages made. Exiting.")
            exit()
        elif overwrite == 'y':
            # Backup old databse file and continue if overwriting accepted
            timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
            backup = "database_" + timestamp + ".db.bak"
            rename('database.db', backup)
            print("Old database backed up to file '" + backup + "'.")
        else:
            # Exit on invalid input
            print("Invalid Input. No Changes were made. Exiting.")
            exit("Input Error")
    
    # Prompt user for council number
    council = input("Council Number (e.g. '35' for 35th Undergraduate Council): ")
    if not council.isdigit() or not int(council) in range(0,100):
        print('Error: Council Number must be a 1-2 digit positive number.\nNo changes were made. Exiting.')
        exit("Input Error")
        
    # Promt user for semester
    semester = input("Current Semester ('F' for fall or 'S' for spring): ")
    if semester != 'S' and semester != 'F':
        print("Error: Semester input must be either an 'S' or 'F'.\nNo changes were made. Exiting.")
        exit("Input Error")
        
    # Prompt User for Current Grant Week in Semester
    week = input("Grant Week in Semester (e.g. '1' for beginning of semester): ")
    if not week.isdigit() or not int(week) in range(1,100):
        print('Error: Grant Week must be a 1-2 digit positive number.\nNo changes were made. Exiting.')
        exit("Input Error")
        
    # Prompt User for Weekly Default Budget
    budget = input("Default Weekly Budget: ")
    if not week.isdigit() or not int(week) > 0:
        print('Error: Default weekly budget must be a postitive whole number.\nNo changes were made. Exiting.')
        exit("Input Error")
        
    # Prompt user for admin email address to create admin user account
    email = input("Administrator Email: ")
    if not email:
        print('Error: Must enter an email address.\nNo changes were made. Exiting.')
        exit("Input Error")
        
    # Prompt user for admin first name to create admin user account
    first_name = input("Administrator First Name: ")
    if not first_name:
        print('Error: Must enter a first name.\nNo changes were made. Exiting.')
        exit("Input Error")
        
    # Prompt user for admin first name to create admin user account
    last_name = input("Administrator Last Name: ")
    if not last_name:
        print('Error: Must enter a last name.\nNo changes were made. Exiting.')
        exit("Input Error")
        
    # Prompt user for admin password to create admin user account
    password = getpass("Administrator Password: ")
    if not password:
        print('Error: Must enter a password.\nNo changes were made. Exiting.')
        exit("Input Error")
    password_verify = getpass("Verify Password: ")
    if password != password_verify:
        print('Error: Passwords do not match.\nNo changes were made. Exiting.')
        exit("Input Error")
        
    # Prompt user for email account username
    email_username = input("Treasurer Email Account Username: ")
    if not email_username:
        print('Error: Must enter an email username.\nNo changes were made. Exiting.')
        exit("Input Error")
        
    # Prompt user for email account password
    email_password = getpass("Treasurer Email Account Password: ")
    if not email_password:
        print('Error: Must enter an email password.\nNo changes were made. Exiting.')
        exit("Input Error")
    
    # Set application context for SQLAlchemy
    db.init_app(app)
    db.app = app
    
    # Create all database with all tables
    db.create_all()
    
    # Add security key configuration
    sec_key = Config('security_key', 'ZmL1kNBW1i')
    db.session.add(sec_key)
    
    # Add Council Number to config
    council_semester = Config('council_semester', council + semester)
    db.session.add(council_semester)
    
    # Add Grant Week to config
    grant_week = Config('grant_week', week)
    db.session.add(grant_week)
    
    # Add Default Weekly Budget
    default_budget = Config('default_budget', budget)
    db.session.add(default_budget)
    
    # Add Email Account Username
    email_username_db = Config('email_username', email_username)
    db.session.add(email_username_db)
    
    # Add Email Account Password
    email_password_db = Config('email_password', email_password)
    db.session.add(email_password_db)
    
    # Add empty number of Grants for current week
    grants_week = Grants_Week(council + semester + '-' + week)
    grants_week.budget = budget
    db.session.add(grants_week)
    
    # Add administrator user account
    admin = create_user(email, first_name, last_name, password, True)
    db.session.add(admin)
    
    # Commit changes to databse
    db.session.commit()
    
    # Print success message
    print("Successfully installed program configuration. Please run flask application to enable the website.")
    
def main():
    install_wizard()

if __name__ == "__main__":
    main()