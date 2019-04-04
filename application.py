#
# application.py
# Nicholas Boucher 2017
#
# Contains the main application code for NOVA. This code maps
# all URL endpoints to FLASK functions
#

import atexit
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify, send_from_directory, Response, stream_with_context
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone, timedelta
from sqlalchemy.sql.expression import or_ as OR, and_ as AND
from flask_login import login_required, fresh_login_required, login_user, logout_user, current_user
from re import match
from flask_mail import Mail, Message
from sys import argv
from pytz import timezone, utc
from flask_migrate import Migrate
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from flask_wtf import Form
from wtforms_sqlalchemy.orm import model_form, model_fields
from os.path import join, exists
from os import makedirs
from werkzeug.utils import secure_filename
from time import strftime
from database_models import *
from helpers import *

# create Flask server
app = Flask(__name__)
# Add support for database migrations
migrate = Migrate(app, db)
# Set uploaded file directory
app.config['UPLOAD_FOLDER'] = join(app.instance_path, "uploads")
if not exists(app.config['UPLOAD_FOLDER']):
    makedirs(app.config['UPLOAD_FOLDER'])

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response
else:
    # Send owed money emails every 14 days if not debug
    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler.add_job(
            func=send_owe_money_emails,
            trigger=IntervalTrigger(days=14),
            id='send_owed_money_emails_job',
            name='Sends Owed Money Emails',
            replace_existing=True)
    # Send receipts emails every 14 days if not debug
    scheduler.add_job(
            func=send_receipt_reminder_emails,
            trigger=IntervalTrigger(days=14),
            id='send_receipts_reminder_emails_job',
            name='Sends Receipts Emails',
            replace_existing=True)
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())

# custom filters
app.jinja_env.filters["usd"] = usd
app.jinja_env.filters["two_decimals"] = number
app.jinja_env.filters["number"] = number
app.jinja_env.filters["suppress_none"] = suppress_none
app.jinja_env.filters["datetime"] = utc_to_east_datetime
app.jinja_env.filters["date"] = utc_to_east_date
app.jinja_env.filters["percentage"] = percentage
app.jinja_env.filters["swap_quotes"] = swap_quotes

# Set cryptographic key for Sessions
install_secret_key(app)

# setup database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Enable authentication
login_manager = LoginManager()
login_manager.init_app(app)

# Tell Authenticator where the login page is located
login_manager.login_view = "login"
login_manager.login_message_category = "message"

# Enable email system
if "installation" not in argv[0]:

    # Due to Flask-Mail Limitations, We must create a seperate App Context for Treasurer Emails
    treasurer_app = Flask("treasurer")

    # Must manually use app context to access database since not handling request
    with app.app_context():

        grants_email_username = Config.query.filter_by(key="grants_email_username").first().value
        grants_email_password = Config.query.filter_by(key="grants_email_password").first().value
        treasurer_email_username = Config.query.filter_by(key="treasurer_email_username").first().value
        treasurer_email_password = Config.query.filter_by(key="treasurer_email_password").first().value
        server_name = Config.query.filter_by(key="server_name").first().value

        # Change the first argument below to configure the sender name on all emails
        app.config['MAIL_DEFAULT_SENDER'] = ('UC Grants', grants_email_username)
        # Let's assume we are using gmail configuration options
        app.config['MAIL_SERVER'] = "smtp.gmail.com"
        app.config['MAIL_PORT'] = 587
        app.config['MAIL_USE_TLS'] = True
        app.config['MAIL_USERNAME'] = grants_email_username
        app.config['MAIL_PASSWORD'] = grants_email_password
        # Set server name for email URLs without app context
        app.config['SERVER_NAME'] = server_name
        # Should help with request file size limits
        app.config['MAIL_MAX_EMAILS'] = 5

    # Setup default Grants Sender Email
    mail = Mail(app)

    # Setup Treasurer Sener Email
    treasurer_app.config['MAIL_DEFAULT_SENDER'] = ('UC Treasurer', treasurer_email_username)
    # Let's assume we are using gmail configuration options
    treasurer_app.config['MAIL_SERVER'] = "smtp.gmail.com"
    treasurer_app.config['MAIL_PORT'] = 587
    treasurer_app.config['MAIL_USE_TLS'] = True
    treasurer_app.config['MAIL_USERNAME'] = treasurer_email_username
    treasurer_app.config['MAIL_PASSWORD'] = treasurer_email_password
    # Set server name for email URLs without app context
    treasurer_app.config['SERVER_NAME'] = server_name
    # Should help with request file size limits
    treasurer_app.config['MAIL_MAX_EMAILS'] = 5
    treasurer_mail = Mail(treasurer_app)

# Define authentication function to lookup users
@login_manager.user_loader
def user_loader(email):
    return User.query.get(email)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=['GET','POST'])
def login():
    """ Allows users to login to the system """

    # User is requesting login page
    if request.method == 'GET':

        # Render page to user
        return render_template('login.html')

    # User is submitting login data
    else:
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        # Verify that email and password were submitted
        if not email or not password:
            flash("Must enter username and password", 'error')
            return render_template('login.html')

        # Query for User
        user = User.query.get(email)

        # Verify that user exists
        if not user:
            flash("Username or password incorrect", 'message')
            return redirect(url_for('login'))

        # Verify that password is correct
        if not verify_password(user, password):
            flash("Username or password incorrect", 'message')
            return redirect(url_for('login'))

        # User has successfully authenticated, log them in
        login_user(user, remember=remember)

        # Redirect user to the correct page
        if user.force_pw_update:
            return redirect(url_for('change_password'))
        else:
            return redirect(url_for('index'))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Successfully logged out", 'message')
    return redirect(url_for('login'))

@app.route('/new_grant')
def new_grant():
    """ Inserts new grant applications into database from query strings passed by qualtrics survey """

    # get arguments from query string
    args = get_grant_args(request.query_string)
    # Verify security key
    sec_key = Config.query.filter_by(key='security_key').first().value
    if not args.get('k') or sec_key != args.get('k')[0]:
        return "Invalid Security Key. You do not have access to this system."

    # This system only works for Upfront and Retroactive UC Grants, so filter others out
    if not args.get('is_upfront') or (args.get('is_upfront')[0] != '1' and args.get('is_upfront')[0] != '2'):
        # This could be updated to do something helpful with notifying on receipt of non-nova application (such as GOHC)
        return redirect(url_for('non_nova_application_submit'))

    # Get Next Grant ID
    council_semester = Config.query.filter_by(key='council_semester').first()
    current_week = Config.query.filter_by(key='grant_week').first()
    grant_prefix = council_semester.value + '-' + current_week.value
    grant_number = Grants_Week.query.filter_by(grant_week=grant_prefix).first()
    # This is not atomic, which seems like a potential problem...
    grant_number.num_grants += 1
    db.session.commit()
    grant_id = grant_prefix + "-" + str(grant_number.num_grants)

    # Create New Grant
    grant = Grant(grant_id)

    # Timezones will be converted to UTC
    eastern = timezone('US/Eastern')

    # Add Grant Values from Parsed Query String
    if args.get('amount_requested'): grant.amount_requested = float(args.get('amount_requested')[0])
    if args.get('is_collaboration'): grant.is_collaboration = (True if args.get('is_collaboration')[0] == "Yes" else False)
    if args.get('collaborators'): grant.collaborators = args.get('collaborators')[0]
    if args.get('collaboration_explanation'): grant.collaboration_explanation = args.get('collaboration_explanation')[0]
    if args.get('contact_first_name'): grant.contact_first_name = args.get('contact_first_name')[0]
    if args.get('contact_last_name'): grant.contact_last_name = args.get('contact_last_name')[0]
    if args.get('contact_email'): grant.contact_email = args.get('contact_email')[0]
    if args.get('contact_phone'): grant.contact_phone = args.get('contact_phone')[0]
    if args.get('contact_role'): grant.contact_role = args.get('contact_role')[0]
    if args.get('is_upfront'): grant.is_upfront = (True if args.get('is_upfront')[0] == "1" else False)
    if args.get('organization'): grant.organization = args.get('organization')[0]
    if args.get('tax_id'): grant.tax_id = args.get('tax_id')[0]
    if args.get('project'): grant.project = args.get('project')[0]
    if args.get('project_description'): grant.project_description = args.get('project_description')[0]
    if args.get('is_event'): grant.is_event = (True if args.get('is_event')[0] == "Event" else False)
    if args.get('project_location'): grant.project_location = args.get('project_location')[0]
    if args.get('project_start'): grant.project_start = eastern.localize(datetime.strptime(args.get('project_start')[0], '%m/%d/%Y')).astimezone(utc)
    if args.get('project_end'): grant.project_end = eastern.localize(datetime.strptime(args.get('project_end')[0], '%m/%d/%Y')).astimezone(utc)
    if args.get('college_attendees'): grant.college_attendees = int(args.get('college_attendees')[0])
    if args.get('facebook_link'): grant.facebook_link = args.get('facebook_link')[0]
    if args.get('revenue1_type'): grant.revenue1_type = args.get('revenue1_type')[0]
    if args.get('revenue1_description'): grant.revenue1_description = args.get('revenue1_description')[0]
    if args.get('revenue1_amount'): grant.revenue1_amount = float(args.get('revenue1_amount')[0])
    if args.get('revenue2_type'): grant.revenue2_type = args.get('revenue2_type')[0]
    if args.get('revenue2_description'): grant.revenue2_description = args.get('revenue2_description')[0]
    if args.get('revenue2_amount'): grant.revenue2_amount = float(args.get('revenue2_amount')[0])
    if args.get('revenue3_type'): grant.revenue3_type = args.get('revenue3_type')[0]
    if args.get('revenue3_description'): grant.revenue3_description = args.get('revenue3_description')[0]
    if args.get('revenue3_amount'): grant.revenue3_amount = float(args.get('revenue3_amount')[0])
    if args.get('revenue4_type'): grant.revenue4_type = args.get('revenue4_type')[0]
    if args.get('revenue4_description'): grant.revenue4_description = args.get('revenue4_description')[0]
    if args.get('revenue4_amount'): grant.revenue4_amount = float(args.get('revenue4_amount')[0])
    if args.get('revenue5_type'): grant.revenue5_type = args.get('revenue5_type')[0]
    if args.get('revenue5_description'): grant.revenue5_description = args.get('revenue5_description')[0]
    if args.get('revenue5_amount'): grant.revenue5_amount = float(args.get('revenue5_amount')[0])
    if args.get('revenue6_type'): grant.revenue6_type = args.get('revenue6_type')[0]
    if args.get('revenue6_description'): grant.revenue6_description = args.get('revenue6_description')[0]
    if args.get('revenue6_amount'): grant.revenue6_amount = float(args.get('revenue6_amount')[0])
    if args.get('revenue7_type'): grant.revenue7_type = args.get('revenue7_type')[0]
    if args.get('revenue7_description'): grant.revenue7_description = args.get('revenue7_description')[0]
    if args.get('revenue7_amount'): grant.revenue7_amount = float(args.get('revenue7_amount')[0])
    if args.get('revenue8_type'): grant.revenue8_type = args.get('revenue8_type')[0]
    if args.get('revenue8_description'): grant.revenue8_description = args.get('revenue8_description')[0]
    if args.get('revenue8_amount'): grant.revenue8_amount = float(args.get('revenue8_amount')[0])
    if args.get('revenue9_type'): grant.revenue9_type = args.get('revenue9_type')[0]
    if args.get('revenue9_amount'): grant.revenue9_amount = float(args.get('revenue9_amount')[0])
    if args.get('revenue10_type'): grant.revenue10_type = args.get('revenue10_type')[0]
    if args.get('revenue10_description'): grant.revenue10_description = args.get('revenue10_description')[0]
    if args.get('revenue10_amount'): grant.revenue10_amount = float(args.get('revenue10_amount')[0])
    if args.get('app_expense1_type'): grant.app_expense1_type = args.get('app_expense1_type')[0]
    if args.get('app_expense1_description'): grant.app_expense1_description = args.get('app_expense1_description')[0]
    if args.get('app_expense1_amount'): grant.app_expense1_amount = float(args.get('app_expense1_amount')[0])
    if args.get('app_expense2_type'): grant.app_expense2_type = args.get('app_expense2_type')[0]
    if args.get('app_expense2_description'): grant.app_expense2_description = args.get('app_expense2_description')[0]
    if args.get('app_expense2_amount'): grant.app_expense2_amount = float(args.get('app_expense2_amount')[0])
    if args.get('app_expense3_type'): grant.app_expense3_type = args.get('app_expense3_type')[0]
    if args.get('app_expense3_description'): grant.app_expense3_description = args.get('app_expense3_description')[0]
    if args.get('app_expense3_amount'): grant.app_expense3_amount = float(args.get('app_expense3_amount')[0])
    if args.get('app_expense4_type'): grant.app_expense4_type = args.get('app_expense4_type')[0]
    if args.get('app_expense4_description'): grant.app_expense4_description = args.get('app_expense4_description')[0]
    if args.get('app_expense4_amount'): grant.app_expense4_amount = float(args.get('app_expense4_amount')[0])
    if args.get('app_expense5_type'): grant.app_expense5_type = args.get('app_expense5_type')[0]
    if args.get('app_expense5_description'): grant.app_expense5_description = args.get('app_expense5_description')[0]
    if args.get('app_expense5_amount'): grant.app_expense5_amount = float(args.get('app_expense5_amount')[0])
    if args.get('app_expense6_type'): grant.app_expense6_type = args.get('app_expense6_type')[0]
    if args.get('app_expense6_description'): grant.app_expense6_description = args.get('app_expense6_description')[0]
    if args.get('app_expense6_amount'): grant.app_expense6_amount = float(args.get('app_expense6_amount')[0])
    if args.get('app_expense7_type'): grant.app_expense7_type = args.get('app_expense7_type')[0]
    if args.get('app_expense7_description'): grant.app_expense7_description = args.get('app_expense7_description')[0]
    if args.get('app_expense7_amount'): grant.app_expense7_amount = float(args.get('app_expense7_amount')[0])
    if args.get('app_expense8_type'): grant.app_expense8_type = args.get('app_expense8_type')[0]
    if args.get('app_expense8_description'): grant.app_expense8_description = args.get('app_expense8_description')[0]
    if args.get('app_expense8_amount'): grant.app_expense8_amount = float(args.get('app_expense8_amount')[0])
    if args.get('app_expense9_type'): grant.app_expense9_type = args.get('app_expense9_type')[0]
    if args.get('app_expense9_description'): grant.app_expense9_description = args.get('app_expense9_description')[0]
    if args.get('app_expense9_amount'): grant.app_expense9_amount = float(args.get('app_expense9_amount')[0])
    if args.get('app_expense10_type'): grant.app_expense10_type = args.get('app_expense10_type')[0]
    if args.get('app_expense10_description'): grant.app_expense10_description = args.get('app_expense10_description')[0]
    if args.get('app_expense10_amount'): grant.app_expense10_amount = float(args.get('app_expense10_amount')[0])
    if args.get('app_expense11_type'): grant.app_expense11_type = args.get('app_expense11_type')[0]
    if args.get('app_expense11_description'): grant.app_expense11_description = args.get('app_expense11_description')[0]
    if args.get('app_expense11_amount'): grant.app_expense11_amount = float(args.get('app_expense11_amount')[0])
    if args.get('app_expense12_type'): grant.app_expense12_type = args.get('app_expense12_type')[0]
    if args.get('app_expense12_description'): grant.app_expense12_description = args.get('app_expense12_description')[0]
    if args.get('app_expense12_amount'): grant.app_expense12_amount = float(args.get('app_expense12_amount')[0])
    if args.get('application_comments'): grant.application_comments = args.get('application_comments')[0]

    # Determine if Small Grant
    # (small_grant_cap and small_grant_expense_types defined in databse_models.py for convenience)
    if nfloat(grant.amount_requested) and nfloat(grant.amount_requested) < small_grant_cap:
        # Parse small grant candidate to rule out grants that are applying for inelligible categories
        expenses = [grant.app_expense1_type,grant.app_expense2_type,grant.app_expense3_type,grant.app_expense4_type,grant.app_expense5_type,grant.app_expense6_type,grant.app_expense7_type,grant.app_expense8_type,grant.app_expense9_type,grant.app_expense10_type,grant.app_expense11_type,grant.app_expense12_type]
        grant.is_small_grant = True
        for expense in expenses:
            if expense and expense not in small_grant_expense_types:
                grant.is_small_grant = False

    # If the organization does not yet exist in our Organizations Database, add the organization
    if grant.organization:
        org = Organization.query.filter_by(name=grant.organization).first()
        if org == None:
            org = Organization(grant.organization)
            db.session.add(org)

    # Commit New Grant to Database
    try:
        db.session.add(grant)
        db.session.commit()
    except IntegrityError:
        return "Error: Grant already exists"

    # Send Confirmation Email
    email_application_submitted(grant)

    return redirect(url_for('application_submitted', grant_id=grant_id))

@app.route('/application-submitted/<grant_id>')
def application_submitted(grant_id):
    return render_template("application_submitted.html", grant_id=grant_id)

@app.route('/application-submit')
def non_nova_application_submit():
    return render_template("application_submitted.html", grant_id=None)

@app.route('/receipts')
def receipts(overwrite = False):
    """ Adds completed project info (including receipts) to existing grant record """

    # Get arguments from query string
    args = get_grant_args(request.query_string)

    # Check for grant_id, which is necessary to update database record
    if not args.get('grant_id'):
        return "Error: No Grant ID submitted"

    # Query for the relevant grant
    grant = Grant.query.filter_by(grant_id=args['grant_id'][0]).first()
    # Return error without updating data if grant does not exist
    if grant == None:
        return "Invalid Grant ID"

    if grant.receipts_submitted and not overwrite:
        return 'Receipts have already been submitted for this grant. To overwrite your previous receipt submission with this one, <a href="/resubmit-receipts?' + request.query_string.decode() + '">click here</a>.'

    if overwrite:
        # Zero out all previous values if overwriting a receipts record
        grant.expense1_description=grant.expense1_amount=grant.expense2_description=grant.expense2_amount=grant.expense3_description=\
        grant.expense3_amount=grant.expense4_description=grant.expense4_amount=grant.expense5_description=grant.expense5_amount=\
        grant.expense6_description=grant.expense6_amount=grant.expense7_description=grant.expense7_amount=grant.expense8_description=\
        grant.expense8_amount=grant.expense9_description=grant.expense9_amount=grant.expense10_description=grant.expense10_amount=\
        grant.expense11_description=grant.expense11_amount=grant.expense12_description=grant.expense12_amount=grant.completed_proj_comments\
        = None

        # update receipt resubmission history
        if grant.receipts_resubmit_history:
            grant.receipts_resubmit_history += ", " + grant.receipts_submit_date.strftime("%Y-%m-%d %H:%M:%S")
        else:
            grant.receipts_resubmit_history = grant.receipts_submit_date.strftime("%Y-%m-%d %H:%M:%S")

    # Parse Recipts images comma-separated list
    if args.get('receipt_images'):
        # Remove all unecessary commas
        receipts = args['receipt_images'][0].replace(', ,', '')
        # trim trailing whitespace
        receipts = receipts.rstrip()
        # Remove final comma (fencepost error)
        if receipts[-1] == ',': receipts = receipts[:-1]
        # trim trailing whitespace
        receipts = receipts.rstrip()
        # Update databse record
        grant.receipt_images = receipts

    # Add Other Grant Values from Parsed Query String
    if args.get('expense1_description'): grant.expense1_description = args.get('expense1_description')[0]
    if args.get('expense1_amount'): grant.expense1_amount = float(args.get('expense1_amount')[0])
    if args.get('expense2_description'): grant.expense2_description = args.get('expense2_description')[0]
    if args.get('expense2_amount'): grant.expense2_amount = float(args.get('expense2_amount')[0])
    if args.get('expense3_description'): grant.expense3_description = args.get('expense3_description')[0]
    if args.get('expense3_amount'): grant.expense3_amount = float(args.get('expense3_amount')[0])
    if args.get('expense4_description'): grant.expense4_description = args.get('expense4_description')[0]
    if args.get('expense4_amount'): grant.expense4_amount = float(args.get('expense4_amount')[0])
    if args.get('expense5_description'): grant.expense5_description = args.get('expense5_description')[0]
    if args.get('expense5_amount'): grant.expense5_amount = float(args.get('expense5_amount')[0])
    if args.get('expense6_description'): grant.expense6_description = args.get('expense6_description')[0]
    if args.get('expense6_amount'): grant.expense6_amount = float(args.get('expense6_amount')[0])
    if args.get('expense7_description'): grant.expense7_description = args.get('expense7_description')[0]
    if args.get('expense7_amount'): grant.expense7_amount = float(args.get('expense7_amount')[0])
    if args.get('expense8_description'): grant.expense8_description = args.get('expense8_description')[0]
    if args.get('expense8_amount'): grant.expense8_amount = float(args.get('expense8_amount')[0])
    if args.get('expense9_description'): grant.expense9_description = args.get('expense9_description')[0]
    if args.get('expense9_amount'): grant.expense9_amount = float(args.get('expense9_amount')[0])
    if args.get('expense10_description'): grant.expense10_description = args.get('expense10_description')[0]
    if args.get('expense10_amount'): grant.expense10_amount = float(args.get('expense10_amount')[0])
    if args.get('expense11_description'): grant.expense11_description = args.get('expense11_description')[0]
    if args.get('expense11_amount'): grant.expense11_amount = float(args.get('expense11_amount')[0])
    if args.get('expense12_description'): grant.expense12_description = args.get('expense12_description')[0]
    if args.get('expense12_amount'): grant.expense12_amount = float(args.get('expense12_amount')[0])
    if args.get('completed_proj_comments'): grant.completed_proj_comments = args.get('completed_proj_comments')[0]

    # Set Submission Metadata
    grant.receipts_submit_date = datetime.now(utc)
    grant.receipts_submitted = True

    # Send notification email to user that the receipts were received
    email_receipts_submitted(grant)

    # Commit database changes
    db.session.commit()
    return 'Your receipts have been received. As always, you can check the status of your grant application <a href="' + url_for("grant", grant_id=grant.grant_id) + '">here</a>.'

@app.route('/resubmit-receipts')
def resubmit_receipts():
    """ Handles the case in which a user would like to re-submit receipts and overwrite previous record """
    return receipts(True)

@app.route('/grant/<grant_id>')
def grant(grant_id):
    """ Retrieves grant info for applicants to track grant progress """

    # Verify that a grant id was specified
    if not grant_id:
        return "Error: No Grant ID specified"

    # Query for grant information
    grant = Grant.query.filter_by(grant_id=grant_id.upper()).first()

    # Check if grant exists in database
    if not grant:
        return "Error: Grant does not exist."

    # See if the edit key was supplied
    if grant.key:
        editable = grant.key == request.args.get('key')
    else:
        # If this grant doesn't have an edit key, anyone can edit it
        editable = True

    # Calculate Progress through grant process for template progress bar
    progress = {'percentage': 0, 'message': ""}
    # Upfront Grants
    if grant.is_upfront:
        # Upfront small grant
        if grant.is_small_grant:
            if grant.hearing_requested and not grant.hearing_occurred:
                progress['percentage'] = 0.9
                progress['message'] = "Hearing Requested."
            elif grant.must_reimburse_uc:
                if grant.reimbursed_uc:
                    progress['percentage'] = 1.0
                    progress['message'] = "Reimbursement Processed. Grant Complete."
                else:
                    progress['percentage'] = 0.9
                    progress['message'] = "Some money unspent. Reimbursement required."
            elif grant.receipts_reviewed:
                progress['percentage'] = 1.0
                progress['message'] = "Receipts Reviewed. Grant Complete."
            elif grant.receipts_submitted:
                progress['percentage'] = 0.85
                progress['message'] = "Receipts Processing"
            elif grant.is_paid:
                progress['percentage'] = 0.68
                if grant.is_direct_deposit == None:
                    progress['message'] = "Submit Receipts"
                elif grant.is_direct_deposit:
                    if grant.pay_date:
                        progress['message'] = "Funds Direct Deposited on " + utc_to_east_date(grant.pay_date) +". Submit Receipts."
                    else:
                        progress['message'] = "Funds Direct Deposited. Submit Receipts."
                else:
                    progress['message'] = "Check Written. Submit Receipts."
            elif grant.council_approved and grant.amount_allocated:
                progress['percentage'] = 0.51
                progress['message'] = "Funds Processing"
            elif grant.council_approved:
                progress['percentage'] = 1.0
                progress['message'] = "Grant Denied"
            elif grant.small_grant_is_reviewed:
                progress['percentage'] = 0.34
                progress['message'] = "Docketed for Council Vote"
            else:
                progress['percentage'] = 0.17
                progress['message'] = "Application Being Reviewed"
        # Upfront non-small grant
        else:
            if grant.hearing_requested and not grant.hearing_occurred:
                progress['percentage'] = 0.9
                progress['message'] = "Hearing Requested."
            elif grant.must_reimburse_uc:
                if grant.reimbursed_uc:
                    progress['percentage'] = 1.0
                    progress['message'] = "Reimbursement Processed. Grant Complete."
                else:
                    progress['percentage'] = 0.9
                    progress['message'] = "Some money unspent. Reimbursement required."
            elif grant.receipts_reviewed:
                progress['percentage'] = 1.0
                progress['message'] = "Receipts Reviewed. Grant Complete."
            elif grant.receipts_submitted:
                progress['percentage'] = 0.84
                progress['message'] = "Receipts Processing"
            elif grant.is_paid:
                progress['percentage'] = 0.70
                if grant.is_direct_deposit == None:
                    progress['message'] = "Submit Receipts"
                elif grant.is_direct_deposit:
                    if grant.pay_date:
                        progress['message'] = "Funds Direct Deposited on " + utc_to_east_date(grant.pay_date) +". Submit Receipts."
                    else:
                        progress['message'] = "Funds Direct Deposited. Submit Receipts."
                else:
                    progress['message'] = "Check Written. Submit Receipts."
            elif grant.council_approved and grant.amount_allocated:
                progress['percentage'] = 0.56
                progress['message'] = "Funds Processing"
            elif grant.council_approved:
                progress['percentage'] = 1.0
                progress['message'] = "Grant Denied"
            elif grant.interview_occurred:
                progress['percentage'] = 0.42
                progress['message'] = "Docketed for Council Vote"
            elif grant.interview_schedule_date:
                progress['percentage'] = 0.28
                progress['message'] = "Interview scheduled for " + utc_to_east_datetime(grant.interview_schedule_date)
            else:
                progress['percentage'] = 0.14
                progress['message'] = "Interview being scheduled"
    # Retroactive Grants
    else:
        # Retroactive small grant
        if grant.is_small_grant:
            if grant.hearing_requested and not grant.hearing_occurred:
                progress['percentage'] = 0.9
                progress['message'] = "Hearing Requested."
            elif grant.is_paid:
                progress['percentage'] = 1.0
                if grant.is_direct_deposit == None:
                    progress['message'] = "Grant Completed."
                elif grant.is_direct_deposit:
                    if grant.pay_date:
                        progress['message'] = "Funds Direct Deposited on " + utc_to_east_date(grant.pay_date)
                    else:
                        progress['message'] = "Funds Direct Deposited into Your Account"
                else:
                    progress['message'] = "Check Written"
            elif grant.receipts_submitted:
                progress['percentage'] = 0.8
                progress['message'] = "Receipts Processing"
            elif grant.council_approved:
                progress['percentage'] = 0.6
                progress['message'] = "Submit Receipts"
            elif grant.small_grant_is_reviewed:
                progress['percentage'] = 0.4
                progress['message'] = "Docketed for Council Vote"
            else:
                progress['percentage'] = 0.2
                progress['message'] = "Application Being Reviewed"
        # Retroactive non-small grant
        else:
            if grant.hearing_requested and not grant.hearing_occurred:
                progress['percentage'] = 0.9
                progress['message'] = "Hearing Requested."
            elif grant.is_paid:
                progress['percentage'] = 1.0
                if grant.is_direct_deposit == None:
                    progress['message'] = "Grant Completed."
                elif grant.is_direct_deposit:
                    if grant.pay_date:
                        progress['message'] = "Funds Direct Deposited on " + utc_to_east_date(grant.pay_date)
                    else:
                        progress['message'] = "Funds Direct Deposited into Your Account"
                else:
                    progress['message'] = "Check Written"
            elif grant.receipts_submitted:
                progress['percentage'] = 0.81
                progress['message'] = "Receipts Processing"
            elif grant.council_approved:
                progress['percentage'] = 0.65
                progress['message'] = "Submit Receipts"
            elif grant.interview_occurred:
                progress['percentage'] = 0.49
                progress['message'] = "Docketed for Council Vote"
            elif grant.interview_schedule_date:
                progress['percentage'] = 0.33
                progress['message'] = "Interview scheduled for " + utc_to_east_datetime(grant.interview_schedule_date)
            else:
                progress['percentage'] = 0.17
                progress['message'] = "Interview being scheduled"

    # Render grant status page to user
    return render_template("grant_status.html", grant=grant, progress=progress, editable=editable)

@app.route('/grant/<grant_id>/application')
def grant_application(grant_id):
    """ Retrieves the original grant application for applicants to review """

    # Verify that a grant id was specified
    if not grant_id:
        return "Error: No Grant ID specified"

    # Query for grant information
    grant = Grant.query.filter_by(grant_id=grant_id.upper()).first()

    # Check if grant exists in database
    if not grant:
        return "Error: Grant does not exist."

    # Render application page to user
    return render_template("grant_application.html", grant=grant)

@app.route('/grant/<grant_id>/allocations')
def grant_allocations(grant_id):
    """ Retrieves the categories and amounts allocated for this grant """

    # Verify that a grant id was specified
    if not grant_id:
        return "Error: No Grant ID specified"

    # Query for grant information
    grant = Grant.query.filter_by(grant_id=grant_id.upper()).first()

    # Check if grant exists in database
    if not grant:
        return "Error: Grant does not exist."

    # Ensure that the council has voted on this before displaying
    if not grant.council_approved:
        return "This information is not yet available."

    # Render application page to user
    return render_template("grant_allocations.html", grant=grant)

@app.route('/interview')
@login_required
def interviews():
    """ Displays a searchable list of grants eligible for interviews """

    # Get list of all grants eligible for interviews
    grants = Grant.query.filter_by(interview_occurred=False, is_small_grant=False).all()

    # Render page to user
    return render_template("interviews.html", grants=grants)

@app.route('/interview/<grant_id>', methods=['GET','POST'])
@login_required
def grant_interview(grant_id):
    """ Displays interview page for FiCom Members to conduct grant interviews and processes responses """

    # Verify that a grant id was specified
    if not grant_id:
        return "Error: No Grant ID specified"

    # Query for grant information
    grant = Grant.query.filter_by(grant_id=grant_id.upper()).first()

    # Check if grant exists in database
    if not grant:
        return "Error: Grant does not exist."

    # Check if we need to return to the grants pack review page
    review = request.args.get('review')

    # User is requesting the interview form
    if request.method == 'GET':

        # If the grant is a small grant, forward to right place
        if grant.is_small_grant:
            return redirect(url_for('small_grant_review', grant_id=grant.grant_id, review=review))

        # Calculate a suggested receipts due date
        if grant.project_end:
            grant.receipts_due = grant.project_end + timedelta(weeks=2)
        else:
            grant.receipts_due = datetime.now() + timedelta(weeks=2)

        # Render page to user
        return render_template('interview_grant.html', grant=grant, review=review)

    # User is submitting the form data
    else:

        # Get Relevant Form Data
        if request.form.get('interviewer_notes'): grant.interviewer_notes = request.form.get('interviewer_notes')
        if request.form.get('food_allocated'): grant.food_allocated = request.form.get('food_allocated', type=float)
        if request.form.get('food_allocated_notes'): grant.food_allocated_notes = request.form.get('food_allocated_notes')
        if request.form.get('travel_allocated'): grant.travel_allocated = request.form.get('travel_allocated', type=float)
        if request.form.get('travel_allocated_notes'): grant.travel_allocated_notes = request.form.get('travel_allocated_notes')
        if request.form.get('publicity_allocated'): grant.publicity_allocated = request.form.get('publicity_allocated', type=float)
        if request.form.get('publicity_allocated_notes'): grant.publicity_allocated_notes = request.form.get('publicity_allocated_notes')
        if request.form.get('materials_allocated'): grant.materials_allocated = request.form.get('materials_allocated', type=float)
        if request.form.get('materials_allocated_notes'): grant.materials_allocated_notes = request.form.get('materials_allocated_notes')
        if request.form.get('venue_allocated'): grant.venue_allocated = request.form.get('venue_allocated', type=float)
        if request.form.get('venue_allocated_notes'): grant.venue_allocated_notes = request.form.get('venue_allocated_notes')
        if request.form.get('decorations_allocated'): grant.decorations_allocated = request.form.get('decorations_allocated', type=float)
        if request.form.get('decorations_allocated_notes'): grant.decorations_allocated_notes = request.form.get('decorations_allocated_notes')
        if request.form.get('media_allocated'): grant.media_allocated = request.form.get('media_allocated', type=float)
        if request.form.get('media_allocated_notes'): grant.media_allocated_notes = request.form.get('media_allocated_notes')
        if request.form.get('admissions_allocated'): grant.admissions_allocated = request.form.get('admissions_allocated', type=float)
        if request.form.get('admissions_allocated_notes'): grant.admissions_allocated_notes = request.form.get('admissions_allocated_notes')
        if request.form.get('hupd_allocated'): grant.hupd_allocated = request.form.get('hupd_allocated', type=float)
        if request.form.get('hupd_allocated_notes'): grant.hupd_allocated_notes = request.form.get('hupd_allocated_notes')
        if request.form.get('personnel_allocated'): grant.personnel_allocated = request.form.get('personnel_allocated', type=float)
        if request.form.get('personnel_allocated_notes'): grant.personnel_allocated_notes = request.form.get('personnel_allocated_notes')
        if request.form.get('other_allocated'): grant.other_allocated = request.form.get('other_allocated', type=float)
        if request.form.get('receipts_due'): grant.receipts_due = datetime.strptime(request.form.get('receipts_due'), '%Y-%m-%d')
        if request.form.get('other_allocated_notes'): grant.other_allocated_notes = request.form.get('other_allocated_notes')
        if request.form.get('is_collaboration_confirmed'): grant.is_collaboration_confirmed = request.form.get('is_collaboration_confirmed')

        if not review:
            # Add Relevant Meta Data
            grant.interview_occurred = True
            grant.interview_date = datetime.now(utc)

            # Add interviewer information for grant record
            grant.interviewer = current_user.first_name + " " + current_user.last_name

            # Send notification email to user
            email_interview_completed(grant)

            # Generate Flashed Success Message
            flash('\'' + grant.organization + '\' Interview Submitted Successfully', 'success')

        else:
            # Generate Flashed Success Message
            flash('\'' + grant.organization + '\' Interview Updated Successfully', 'success')

        # Commit Changes to Database
        db.session.commit()

        if review:
            return redirect(url_for('grants_pack_edit_pack', grants_pack=review))
        else:
            return redirect(url_for('interviews'))

@app.route('/small-grant-review')
@login_required
def small_grants():
    """ Displays a list of grants eligible for small-grant processing """

    # Get list of all small-grant elligible grants
    grants = Grant.query.filter_by(is_small_grant=True, small_grant_is_reviewed=False).all()

    # Render page to user
    return render_template("small_grants.html", grants=grants)

@app.route('/small-grant-review/<grant_id>', methods=['GET','POST'])
@login_required
def small_grant_review(grant_id):
    """ Displays review page for FiCom Members to conduct small grant reviews and processes responses """

    # Verify that a grant id was specified
    if not grant_id:
        return "Error: No Grant ID specified"

    # Query for grant information
    grant = Grant.query.filter_by(grant_id=grant_id.upper()).first()

    # Check if grant exists in database
    if not grant:
        return "Error: Grant does not exist."

    # Check if we need to return to the grants pack review page
    review = request.args.get('review')

    # User is requesting the interview form
    if request.method == 'GET':

        # If the grant is not a small grant, forward to right place
        if not grant.is_small_grant:
            return redirect(url_for('grant_interview', grant_id=grant.grant_id, review=review))

        # Render page to user
        return render_template('review_small_grant.html', grant=grant, review=review)

    # User is submitting the form data
    else:

        # Get Relevant Form Data
        if request.form.get('interviewer_notes'): grant.interviewer_notes = request.form.get('interviewer_notes')
        if request.form.get('food_allocated'): grant.food_allocated = request.form.get('food_allocated', type=float)
        if request.form.get('food_allocated_notes'): grant.food_allocated_notes = request.form.get('food_allocated_notes')
        if request.form.get('publicity_allocated'): grant.publicity_allocated = request.form.get('publicity_allocated', type=float)
        if request.form.get('publicity_allocated_notes'): grant.publicity_allocated_notes = request.form.get('publicity_allocated_notes')
        if request.form.get('is_collaboration_confirmed'): grant.is_collaboration_confirmed = request.form.get('is_collaboration_confirmed')
        if request.form.get('receipts_due'): grant.receipts_due = datetime.strptime(request.form.get('receipts_due'), '%Y-%m-%d')

        # Add Relevant Meta Data
        grant.small_grant_is_reviewed = True
        grant.small_grant_review_date = datetime.now(utc)

        # Add interviewer information for grant record
        grant.small_grant_reviewer = current_user.first_name + " " + current_user.last_name

        # Commit Changes to Databse
        db.session.commit()

        # Generate Flashed Success Message
        flash('\'' + grant.organization + '\' Small Grant Review Submitted Successfully', 'success')

        if review:
            return redirect(url_for('grants_pack_edit_pack', grants_pack=review))
        else:
            return redirect(url_for('small_grants'))

@app.route('/grants-pack/edit', methods=['GET','POST'])
@login_required
@admin_required
def grants_pack_edit(grants_pack=None):
    """ Displays page to review and select grants that are elligible for adding to a grants pack,
        and processes updates POSTed by the page """

    # User is requesting the form page
    if request.method == 'GET':
        # Create Variable for holding grants_pack row from DB
        grants_pack_db = None
        if grants_pack:
            # If user-specified grants pack does not exist, return an error
            grants_pack_db = Grants_Week.query.filter_by(grant_week=grants_pack).first()
            if not grants_pack_db:
                return "Grants Pack " + grants_pack + " does not exist.",400
        # Default to current Grants Pack
        else:
            # Get Current Grants Pack
            council_semester = Config.query.filter_by(key='council_semester').first()
            current_week = Config.query.filter_by(key='grant_week').first()
            grants_pack = council_semester.value + '-' + current_week.value
            grants_pack_db = Grants_Week.query.filter_by(grant_week=grants_pack).first()

        # Ensure that the grants pack has not been locked (by approved council vote)
        if grants_pack_db.grants_pack_finalized:
            return "This grants pack has already been finalized and approved by the council."

        # query for all grants currently without a grants pack
        orphan_grants = Grant.query.filter(OR(AND(Grant.grants_pack==None,Grant.interview_occurred==True), AND(Grant.grants_pack==None,Grant.small_grant_is_reviewed==True))).all()
        child_grants = Grant.query.filter_by(grants_pack=grants_pack).all()

        # Render page to user
        return render_template('grants_pack_edit.html', orphan_grants=orphan_grants, child_grants=child_grants, grants_pack=grants_pack)

    # User is POSTing form data updates back to the server
    else:
        # Ensure that that grant_pack value was sent
        grants_pack = request.json.get('grants_pack')
        if grants_pack:
            # Ensure that at least one grant was sent
            grants = request.json.get('grants')
            if grants and len(grants) > 0:
                # Ensure that the grants pack has not been locked (by approved council vote)
                grants_pack_db = Grants_Week.query.filter_by(grant_week=grants_pack).first()
                if grants_pack_db.grants_pack_finalized:
                    return "This grants pack has already been finalized and approved by the council.",400
                # For each grant, update its value in the database
                for grant in grants:
                    grant_id = grant.get('grant_id')
                    selected = grant.get('selected')
                    # Ensure that grant_id was provided and selected is valid
                    if grant_id and selected != None:
                        # This slightly ugly syntax uses far fewer SQL calls than the alternative
                        if selected:
                            Grant.query.filter(Grant.grant_id==grant_id).update({ "grants_pack" : grants_pack })
                        else:
                            Grant.query.filter(Grant.grant_id==grant_id).update({ "grants_pack" : None })
                        db.session.commit()
                return "OK"
        # On failure, return error with HTTP 400 "Bad Request" Status Code
        return 'Error',400

@app.route('/grants-pack/<grants_pack>/edit')
@login_required
@admin_required
def grants_pack_edit_pack(grants_pack):
    """ Allows editing of a specific grants pack """
    return grants_pack_edit(grants_pack)

@app.route('/grants-pack/cuts', methods=['GET','POST'])
@login_required
@admin_required
def grants_pack_cuts(grants_pack=None):
    """ Displays a page to the user with the calculated cut amounts """

    # User is requesting the form page
    if request.method == 'GET':
        # Create Variable for holding grants_pack row from DB
        grants_pack_db = None
        if grants_pack:
            # If user-specified grants pack does not exist, return an error
            grants_pack_db = Grants_Week.query.filter_by(grant_week=grants_pack).first()
            if not grants_pack_db:
                return "Grants Pack " + grants_pack + " does not exist.",400
        # Default to current Grants Pack
        else:
            # Get Current Grants Pack
            council_semester = Config.query.filter_by(key='council_semester').first()
            current_week = Config.query.filter_by(key='grant_week').first()
            grants_pack = council_semester.value + '-' + current_week.value
            grants_pack_db = Grants_Week.query.filter_by(grant_week=grants_pack).first()

        # Ensure that the grants pack has not been locked (by approved council vote)
        if grants_pack_db.grants_pack_finalized:
            return "This grants pack has already been finalized and approved by the council."

        # Get all grants in grants pack from the DB
        grants = Grant.query.filter_by(grants_pack=grants_pack).all()

        # Get this grants pack's budget
        budget = grants_pack_db.budget

        # Calculate expendature for this week
        allocated = 0
        cut_immune = 0
        for grant in grants:
            # Sum grant
            grant.amount_allocated = 0
            if grant.food_allocated: grant.amount_allocated += grant.food_allocated
            if grant.travel_allocated: grant.amount_allocated += grant.travel_allocated
            if grant.publicity_allocated: grant.amount_allocated += grant.publicity_allocated
            if grant.materials_allocated: grant.amount_allocated += grant.materials_allocated
            if grant.venue_allocated: grant.amount_allocated += grant.venue_allocated
            if grant.decorations_allocated: grant.amount_allocated += grant.decorations_allocated
            if grant.media_allocated: grant.amount_allocated += grant.media_allocated
            if grant.admissions_allocated: grant.amount_allocated += grant.admissions_allocated
            if grant.hupd_allocated: grant.amount_allocated += grant.hupd_allocated
            if grant.personnel_allocated: grant.amount_allocated += grant.personnel_allocated
            if grant.other_allocated: grant.amount_allocated += grant.other_allocated
            # Add to allocated costs
            allocated += grant.amount_allocated
            # If immune from cuts, add to cut_immune
            if grant.is_collaboration_confirmed:
                cut_immune += grant.amount_allocated

        # See if we went overbudget, and calculate cut percentage
        cuts = 0
        if allocated > budget:
            deductable = allocated - cut_immune
            remaining = budget - cut_immune
            cuts = 1.0 - (remaining / deductable)

        # Apply the recommended cuts for each grant
        for grant in grants:
            if grant.is_collaboration_confirmed:
                grant.percentage_cut = 0.0
            else:
                grant.percentage_cut = cuts

        percentage_cut = round(100 * cuts, 2)
        cut_multiplier = 1.0 - cuts

        return render_template('grants_pack_cuts.html', grants=grants, grants_pack=grants_pack, budget=budget, allocated=allocated, cut_immune=cut_immune, percentage_cut=percentage_cut, cut_multiplier=cut_multiplier)

    # User is POSTing form data updates back to the server
    else:
        # Format posted data and get grant_pack value
        values = dict(request.form)
        grants_pack = values.pop('grants_pack')[0]
        # Update Weekly running total while calculating grants
        grant_week = Grants_Week.query.filter_by(grant_week=grants_pack).first()
        grant_week.allocated = 0.0
        grant_week.requested = 0.0
        # Process each grant
        for grant_id,cut in values.items():
            # Get the percentage gut in the correct format
            cut = float(cut[0])
            # Update grant record with cut and final allocated amount
            grant = Grant.query.filter_by(grant_id=grant_id).first()
            # Sum grant
            allocated = 0
            if grant.food_allocated: allocated += grant.food_allocated
            if grant.travel_allocated: allocated += grant.travel_allocated
            if grant.publicity_allocated: allocated += grant.publicity_allocated
            if grant.materials_allocated: allocated += grant.materials_allocated
            if grant.venue_allocated: allocated += grant.venue_allocated
            if grant.decorations_allocated: allocated += grant.decorations_allocated
            if grant.media_allocated: allocated += grant.media_allocated
            if grant.admissions_allocated: allocated += grant.admissions_allocated
            if grant.hupd_allocated: allocated += grant.hupd_allocated
            if grant.personnel_allocated: allocated += grant.personnel_allocated
            if grant.other_allocated: allocated += grant.other_allocated
            # Save cut and calculate final amount allocated
            grant.percentage_cut = cut
            grant.amount_allocated = round((100 - cut) / 100 * allocated, 2)
            grant_week.allocated += grant.amount_allocated
            grant_week.requested += grant.amount_requested

        # Notify user of successful submit
        flash("Grants Pack " + grants_pack + " submitted successfully.", 'success')

        # Get the current council semester and grants week
        grant_week_config = Config.query.filter_by(key="grant_week").first()
        if not grant_week_config:
            return "Error: grant_week not defined in Config database"
        council_semester = Config.query.filter_by(key="council_semester").first()
        if not council_semester:
            return "Error: council semester not defined in config database"

        # If this was the current grants_pack, create a new one and set it as current
        if grant_week.grant_week == council_semester.value + '-' + grant_week_config.value:

            # Get the next uncreated grants_week in the semester
            next_grant_week = int(grant_week_config.value) + 1
            while Grants_Week.query.filter_by(grant_week=(council_semester.value + '-' + str(next_grant_week))).first() != None:
                next_grant_week += 1

            # Query for default budget
            budget = Config.query.filter_by(key="default_budget").first()
            if not budget:
                "Error: Default Budget not defined in Config database"

            # Create the new grants week
            next_grant_week_db = Grants_Week(council_semester.value + '-' + str(next_grant_week))
            next_grant_week_db.budget = float(budget.value)
            db.session.add(next_grant_week_db)

            # Update the config
            grant_week_config.value = str(next_grant_week)

            # Display notice to user of new grants pack
            flash("Grants Pack " + next_grant_week_db.grant_week + " created and set as the current grants pack.", "warning")

        # Commit all changes at once
        db.session.commit()

        return redirect(url_for('grants_packs'))

@app.route('/grants-pack/<grants_pack>/cuts')
@login_required
@admin_required
def grants_pack_cuts_pack(grants_pack):
    """ Allows calculating cuts of any given grants pack """
    return grants_pack_cuts(grants_pack)

@app.route('/grants-pack')
@login_required
@admin_required
def grants_packs():
    """ Shows page listing all grants packs and their status """
    # Query for all existing grants packs
    grants_packs = Grants_Week.query.order_by(Grants_Week.grant_week.desc()).all()
    # Render the page to the user
    return render_template('grants_packs.html', grants_packs=grants_packs)

@app.route('/grants-pack/<grants_pack>/view')
@login_required
@admin_required
def grants_pack_view_pack(grants_pack):
    """ Gives a basic overview page containing the grants pack data """

    # Ensure that grants_pack was specified
    if not grants_pack:
        return "Grants Pack not specified"

    # Query for grants pack
    grants_pack_db = Grants_Week.query.filter_by(grant_week=grants_pack).first()
    # Verify that grants_pack exists
    if not grants_pack_db:
        return "Grants Pack Does Not Exist"

    # Verify that that grants pack has been allocated already
    if not grants_pack_db.allocated:
        return redirect(url_for('grants_pack_edit_pack', grants_pack=grants_pack))

    # Query for all associated grants
    grants = Grant.query.filter_by(grants_pack=grants_pack)

    # Render page to user
    return render_template('grants_pack_view.html', grants_pack=grants_pack_db, grants=grants)

@app.route('/grants_pack/<grants_pack>/approve', methods=['GET','POST'])
@login_required
@admin_required
def grants_pack_council_approve(grants_pack):
    """ Allows the user to verify that a grants pack has been approved by the council """

    # Verify that grants pack was specified
    if not grants_pack:
        return "Must specify grants pack"

    # Verify that grants pack exists
    grants_pack_db = Grants_Week.query.filter_by(grant_week=grants_pack).first()
    if not grants_pack_db:
        return "Grants pack " + grants_pack + " does not exist."

    # Verify that the grants pack has been allocated before approving
    if grants_pack_db.allocated == None:
        return "Grant pack must be allocated via editing before it can be approved."

    # User is requesting the confirmation page
    if request.method == 'GET':

        # Render the confirmation page to the user
        return render_template('grants_pack_council_approve.html', grants_pack=grants_pack_db)

    # User is POSTing the confirmation to the server
    else:

        # Query for each grant in the grants pack
        grants = Grant.query.filter_by(grants_pack=grants_pack).all()

        # Update each grant to council approved & send email
        for grant in grants:
            grant.council_approved = True
            if grant.amount_allocated == 0:
                # Send "denied" notification email to user
                email_application_denied(grant)
            else:
                # Send "passed" notification email to user
                email_application_passed(grant)

        # Update database to approve grants pack
        grants_pack_db.grants_pack_finalized = True

        # Commit changes to database
        db.session.commit()

        # Display message to user that the grants pack has been approved
        flash("Grants Pack " + grants_pack + " has been successfully marked as approved.", 'success')

        # Redirect to grants packs listing
        return redirect(url_for('grants_packs'))

@app.route('/search', methods=['GET','POST'])
def search():
    """ Allows the user to search for grants by Organization, Project, or Grant ID """

    # Get Security Key
    sec_key = Config.query.filter_by(key="security_key").first()
    if sec_key == None:
        return "Security Key not set."

    # User is requesting the search form
    if request.method == 'GET':

        # Render the page to the user
        return render_template('search.html', k=sec_key.value)

@app.route('/search/organizations')
def organizations():
    """ Provides an API endpoint which returns a list of all organizations in JSON """

    # Get Security Key
    sec_key = Config.query.filter_by(key="security_key").first()
    if sec_key == None:
        return "Security Key not set."

    # Verify the security key
    if request.args.get('k') != sec_key.value:
        return "Invlalid Security Key. You do not have access to this system."

    # See if there is a query
    query = request.args.get('query')
    if query:
        # Search for the query
        orgs = [i.name for i in Organization.query.filter(Organization.name.like('%' + query + '%'))]
    else:
        # Respond with JSON of all organizations
        orgs = [i.name for i in Organization.query.all()]

    # Return the JSON response
    return jsonify(orgs)

@app.route('/search/projects')
def projects():
    """ Provides an API endpoint for which projects can be queried """

    # Get Security Key
    sec_key = Config.query.filter_by(key="security_key").first()
    if sec_key == None:
        return "Security Key not set."

    # Verify the security key
    if request.args.get('k') != sec_key.value:
        return "Invlalid Security Key. You do not have access to this system."

    # See if there is a query
    query = request.args.get('query')
    if query:
        # Search for the query
        projects = [grant.project for grant in Grant.query.filter(Grant.project.like('%' + query + '%'))]
    else:
        # If there is no query, return an empty response
        return "[]"

    # Return the JSON response
    return jsonify(projects)

@app.route('/search/lookup-grants')
def lookup_grants():
    """ API endpoint that returns a list of all grants from an organization """

    # Get Security Key
    sec_key = Config.query.filter_by(key="security_key").first()
    if sec_key == None:
        return "Security Key not set."

    # Verify the security key
    if request.args.get('k') != sec_key.value:
        return "Invlalid Security Key. You do not have access to this system."

    # Get Search criteria
    query = request.args.get('query')

    # Ensure that query was specified
    if not query:
        return "Must specify query"

    # Query for grants by organization
    org_grants = Grant.query.filter_by(organization=query).all()

    # Build list of grant data for JSON serialization
    results = list(map(serialize_grant, org_grants))

    # Query for grants by project name
    project_grants = Grant.query.filter_by(project=query).all()

    # Add grant if it exists
    if grant:
        results += list(map(serialize_grant, project_grants))

    # Return results in JSON form
    return jsonify(results)

@app.route('/treasurer')
@login_required
@admin_required
def review_receipts():
    """ Displays a page to the user of grants that are ready to have receipts verified """

    # Query for relevant grants
    retroactive_grants = Grant.query.filter_by(council_approved=True,is_upfront=False,receipts_submitted=True,is_paid=False).all()
    upfront_grants = Grant.query.filter(AND(AND(Grant.council_approved==True,Grant.is_upfront==True),AND(Grant.is_paid==False,Grant.amount_allocated!=0))).all()
    upfront_receipts = Grant.query.filter_by(council_approved=True,is_upfront=True,is_paid=True,receipts_submitted=True,receipts_reviewed=False).all()

    # Query for orgs in bad standing
    no_receipts = Grant.query.filter(AND(AND(AND(AND(AND(AND(Grant.council_approved==True,Grant.amount_allocated>0),Grant.receipts_submitted==False), Grant.receipts_due < datetime.now()), Grant.amount_dispensed>0), Grant.reimbursed_uc==False, OR(OR(Grant.hearing_requested==False,Grant.hearing_requested==None),Grant.hearing_occurred==True)))).all()
    unspent_money = Grant.query.filter(AND(AND(AND(AND(Grant.council_approved==True,Grant.amount_allocated>0),Grant.must_reimburse_uc==True),Grant.reimbursed_uc==False, OR(OR(Grant.hearing_requested==False,Grant.hearing_requested==None),Grant.hearing_occurred==True)))).all()
    hearings = Grant.query.filter(AND(Grant.hearing_requested==True,Grant.hearing_occurred==False))
    bad_orgs = set([x.organization for x in no_receipts] + [x.organization for x in unspent_money] + [x.organization for x in hearings])

    # Render grants page to the user
    return render_template('review_receipts.html', retroactive_grants=retroactive_grants,upfront_grants=upfront_grants,upfront_receipts=upfront_receipts, bad_orgs=bad_orgs)

@app.route('/treasurer/<grant_id>', methods=['GET','POST'])
@login_required
@admin_required
def review_grant_receipts(grant_id):
    """ Displays receipts for specified grant to the treasurer for review """

    # Ensure that grant_id was specified
    if not grant_id:
        return "Must specify grant id."

    # Query for grant
    grant = Grant.query.filter_by(grant_id=grant_id).first()

    # Ensure that grant exists
    if not grant:
        return "Grant " + grant_id + " does not exist."

    # Ensure that the grant is ready for treasurer review
    if not grant.council_approved or not grant.receipts_submitted or grant.is_paid:
        return "Grant " + grant_id + " is not elligible to be reviewed by the Treasurer."

    # User is requesting grant page
    if request.method == 'GET':

        # Query for the organization information and validate
        organization = Organization.query.filter_by(name=grant.organization).first()
        if not organization:
            return "Internal Error: Organization not listed in database"

        # Ensure that the percentage cut was specified
        if grant.percentage_cut == None:
            return "Error: No percentage cut associated with grant."

        # Apply funding cuts to local variable (for page rendering) without committing to DB
        cut_multiplier = (100.0 - grant.percentage_cut) / 100
        if grant.food_allocated: grant.food_allocated *= cut_multiplier
        if grant.travel_allocated: grant.travel_allocated *= cut_multiplier
        if grant.publicity_allocated: grant.publicity_allocated *= cut_multiplier
        if grant.materials_allocated: grant.materials_allocated *= cut_multiplier
        if grant.venue_allocated: grant.venue_allocated *= cut_multiplier
        if grant.decorations_allocated: grant.decorations_allocated *= cut_multiplier
        if grant.media_allocated: grant.media_allocated *= cut_multiplier
        if grant.admissions_allocated: grant.admissions_allocated *= cut_multiplier
        if grant.hupd_allocated: grant.hupd_allocated *= cut_multiplier
        if grant.personnel_allocated: grant.personnel_allocated *= cut_multiplier
        if grant.other_allocated: grant.other_allocated *= cut_multiplier

        receipts = grant.receipt_images.split(", ") if grant.receipt_images else []

        # Render the template to the user
        return render_template('review_grant_receipts.html', grant=grant, receipts=receipts, organization=organization)

    # User is submitting form
    else:
        # Updates grant information
        grant.is_paid = True
        grant.receipts_reviewed = True
        grant.pay_date = datetime.now(utc)
        grant.receipts_reviewer = current_user.first_name + " " + current_user.last_name
        grant.amount_dispensed = grant.amount_spent = float(request.form.get('amount'))
        grant.treasurer_notes = request.form.get('treasurer_notes')
        if request.form.get('is_check'):
            grant.is_direct_deposit = False
            grant.check_number = request.form.get('check_number')

            # Send notification email to user to pickup check
            email_check(grant)

        else:
            grant.is_direct_deposit = True

            # Send notification email to user that direct deposit occurred
            email_direct_deposit(grant)

        # Commit all changes to database
        db.session.commit()

        # Display success message to user
        flash("Successfully finalized Grant " + grant.grant_id + ' "' + grant.project + '".', 'success')

        # Redirect to treasurer page
        return redirect(url_for('review_receipts'))

@app.route('/settings')
@login_required
@admin_required
def settings():
    """ Provides a page for grants-pack advancing, user
        management, and general settings. """

    # Query for all users
    users = User.query.all()

    # Query for default weekly budget
    default_budget = Config.query.filter_by(key="default_budget").first()
    if not default_budget:
        return "Error: Default budget not specified in database"

    # Query for emails enabled
    enable_email = Config.query.filter_by(key="enable_email").first()
    if not enable_email:
        return "Error: enable_email not specified in database"

    # Query for grants email username
    grants_email_username = Config.query.filter_by(key="grants_email_username").first()
    if not grants_email_username:
        return "Error: grants_email_username not specified in database"

    # Query for treasurer email username
    treasurer_email_username = Config.query.filter_by(key="treasurer_email_username").first()
    if not treasurer_email_username:
        return "Error: treasurer_email_username not specified in database"

    # Query for treasurer name
    treasurer_name = Config.query.filter_by(key="treasurer_name").first()
    if not treasurer_name:
        return "Error: treasurer_name not specified in database"

    # Query for current council semester
    council_semester = Config.query.filter_by(key="council_semester").first()
    if not council_semester:
        return "Error: Council semester not specified in database"

    # Query for current grants week
    grant_week = Config.query.filter_by(key="grant_week").first()
    if not grant_week:
        return "Error: Grant week not specified in database"

    grants_pack = council_semester.value + '-' + grant_week.value

    # Render page to user
    return render_template('settings.html', users=users, default_budget=default_budget.value, council_semester=council_semester.value, grants_pack=grants_pack, enable_email=enable_email.value, grants_email_username=grants_email_username.value, treasurer_email_username=treasurer_email_username.value, treasurer_name=treasurer_name.value)

@app.route('/settings/edit-user', methods=['GET','POST'])
@login_required
@admin_required
def edit_user():
    """ Provides an interface where an administrator can edit users """

    # Get the user from the arguments
    email = request.args.get('user')

    # Verify that the user was specified
    if not email:
        return "Must specify a user"

    # Query for the user
    user = User.query.filter_by(email=email).first()

    # Ensure that user exists
    if not user:
        return "User does not exist"

    # User is requesting form
    if request.method == 'GET':

        # Render page to user
        return render_template('edit_user.html', user=user)

    # User is submitting form data
    else:

        # Get all form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        if request.form.get('admin'):
            admin = True
        else:
            admin = False
        if current_user.treasurer and request.form.get('treasurer'):
            treasurer = True
        else:
            treasurer = False
        if request.form.get('reset_pw'):
            reset_pw = True
        else:
            reset_pw = False

        # Verify that required fields have been completed
        if not first_name or not last_name or not email:
            flash("All fields are required", 'error')
            return render_template('edit_user.html', user=user)

        # Update value
        user.first_name = first_name
        user.last_name = last_name
        user.email = email

        # Ensure current user isn't changing important details about self
        if user != current_user:

            # Update Admin value
            user.admin = admin

            # Update Treasurer value
            user.treasurer = treasurer

            # Reset user password if requested
            if reset_pw:
                user.pw_hash = encrypt("password", user.salt)
                user.force_pw_update = True

        # Commit changes to database
        db.session.commit()

        # Display success message
        flash('User "' + user.first_name + ' ' + user.last_name + '" Updated Successfully')

        return redirect(url_for('settings'))

@app.route('/settings/add-user', methods=['GET','POST'])
@login_required
@admin_required
def add_user():
    """ Allows an admin to add users to the system """

    # User is requesting form
    if request.method == 'GET':

        # Render page to user
        return render_template('add_user.html')

    # User is submitting form data
    else:
        # Get all form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        if request.form.get('admin'):
            admin = True
        else:
            admin = False
        if current_user.treasurer and request.form.get('treasurer'):
            treasurer = True
        else:
            treasurer = False

        # Verify that required fields have been completed
        if not first_name or not last_name or not email:
            flash("All fields are required", 'error')
            return render_template('add_user.html')

        # Create user
        user = create_user(email, first_name, last_name, "password", admin)

        # Add treasurer permissions
        user.treasurer = treasurer

        # Add new user to database
        db.session.add(user)
        db.session.commit()

        # Display success message
        flash('User "' + user.first_name + ' ' + user.last_name + '" Created Successfully')

        return redirect(url_for('settings'))

@app.route('/settings/delete-user', methods=['GET','POST'])
@login_required
@admin_required
def delete_user():
    """ Allows an admin to remove users from the system """

    # Get the user from the arguments
    email = request.args.get('user')

    # Verify that the user was specified
    if not email:
        return "Must specify a user"

    # Query for the user
    user = User.query.filter_by(email=email).first()

    # Ensure that user exists
    if not user:
        return "User does not exist"

    # Ensure that user is not deleting their own account
    if user == current_user:
        return "Cannot delete current user account"

    # Ensure non-treasurers cannot delete treasurers
    if user.treasurer and not current_user.treasurer:
        return "A non-treasurer cannot delete a treasurer"

    # User is requesting form
    if request.method == 'GET':

        # Render page to user
        return render_template('delete_user.html', user=user)

    # User is submitting form data
    else:

        # Remove the user from the database
        db.session.delete(user)
        db.session.commit()

        # Dispaly success message
        flash('User "' + user.first_name + ' ' + user.last_name + '" Deleted Successfully')

        # Redirect to settings page
        return redirect(url_for('settings'))

@app.route('/settings/default-budget', methods=['POST'])
@login_required
@admin_required
def default_budget():
    """ Allows an administrator to set the default budget """

    # Get budget value from form and verify its existence
    budget = request.form.get('default_budget')
    if not budget:
        return "Budget value not specified"

    # Verify valid content
    if not isfloat(budget):
        return "Invalid budget quantity"

    # Query for default weekly budget
    def_budget = Config.query.filter_by(key="default_budget").first()

    if not def_budget:
        return "Error: Default budget not specified in database"

    # Update value and commit changes
    def_budget.value = budget
    db.session.commit()

    # Display success message
    flash("Successfully updated default budget")

    # Send user to settings page
    return redirect(url_for('settings'))

@app.route('/settings/enable-emails', methods=['POST'])
@login_required
@admin_required
def enable_email():
    """ Allows an administrator to set whether emails are sent """

    # Get email value from form
    if request.form.get('enable_email'):
        enable = 1
    else:
        enable = 0
    # Query for enable_email key
    email_key = Config.query.filter_by(key="enable_email").first()

    if not email_key:
        return "Error: enable_email not specified in database"

    # Update value and commit changes
    email_key.value = enable
    db.session.commit()

    # Display success message
    flash("Successfully updated email enabled value")

    # Send user to settings page
    return redirect(url_for('settings'))

@app.route('/settings/grants-email-username', methods=['POST'])
@login_required
@admin_required
def grants_email_username():
    """ Allows an administrator to set the username for the grants email """

    # Get email value from form
    email = request.form.get("grants_email_username")
    if not email:
        flash("No grants email username specified.", 'error')
        return redirect(url_for('settings'))

    # Query for email key
    email_key = Config.query.filter_by(key="grants_email_username").first()

    if not email_key:
        return "Error: grants_email_username not specified in database"

    # Update value and commit changes
    email_key.value = email
    db.session.commit()

    # Display success message
    flash("Successfully updated grants email address")

    # Send user to settings page
    return redirect(url_for('settings'))

@app.route('/settings/grants-email-password', methods=['POST'])
@login_required
@admin_required
def grants_email_password():
    """ Allows an administrator to set the password for the grants email """

    # Get password value from form
    password = request.form.get("grants_email_password")
    if not password:
        flash("No grants email password specified.", 'error')
        return redirect(url_for('settings'))

    # Query for password key
    password_key = Config.query.filter_by(key="grants_email_password").first()

    if not password_key:
        return "Error: grants_email_password not specified in database"

    # Update value and commit changes
    password_key.value = password
    db.session.commit()

    # Display success message
    flash("Successfully updated grants email password")

    # Send user to settings page
    return redirect(url_for('settings'))

@app.route('/settings/treasurer-email-username', methods=['POST'])
@login_required
@admin_required
def treasurer_email_username():
    """ Allows an administrator to set the username for the treasurer email """

    # Get email value from form
    email = request.form.get("treasurer_email_username")
    if not email:
        flash("No treasurer email username specified.", 'error')
        return redirect(url_for('settings'))

    # Query for email key
    email_key = Config.query.filter_by(key="treasurer_email_username").first()

    if not email_key:
        return "Error: treasurer_email_username not specified in database"

    # Update value and commit changes
    email_key.value = email
    db.session.commit()

    # Display success message
    flash("Successfully updated treasurer email address")

    # Send user to settings page
    return redirect(url_for('settings'))

@app.route('/settings/treasurer-email-password', methods=['POST'])
@login_required
@admin_required
def treasurer_email_password():
    """ Allows an administrator to set the password for the treasurer email """

    # Get password value from form
    password = request.form.get("treasurer_email_password")
    if not password:
        flash("No treasurer email password specified.", 'error')
        return redirect(url_for('settings'))

    # Query for password key
    password_key = Config.query.filter_by(key="treasurer_email_password").first()

    if not password_key:
        return "Error: treasurer_email_password not specified in database"

    # Update value and commit changes
    password_key.value = password
    db.session.commit()

    # Display success message
    flash("Successfully updated treasurer email password")

    # Send user to settings page
    return redirect(url_for('settings'))

@app.route('/settings/treasurer-name', methods=['POST'])
@login_required
@admin_required
def treasurer_name():
    """ Allows an administrator to set the treasurer name """

    # Get name value from form
    name = request.form.get("treasurer_name")
    if not name:
        flash("No treasurer name specified.", 'error')
        return redirect(url_for('settings'))

    # Query for name key
    name_key = Config.query.filter_by(key="treasurer_name").first()

    if not name_key:
        return "Error: treasurer_name not specified in database"

    # Update value and commit changes
    name_key.value = name
    db.session.commit()

    # Display success message
    flash("Successfully updated treasurer name")

    # Send user to settings page
    return redirect(url_for('settings'))

@login_required
@app.route('/change-password', methods=['GET','POST'])
def change_password():
    """ Allows any given user to change their password """

    # User is requesting form
    if request.method == 'GET':

        # Render form to user
        return render_template('change_password.html')

    # User is submitting form
    else:

        # Get form data
        password = request.form.get('password')
        confirm = request.form.get('password_confirmation')

        # Ensure that both passwords exist and match
        if not password or not confirm:
            return "Must supply both password and confirmation"
        if password != confirm:
            flash("Passwords do not match", 'error')
            return render_template('change_password.html')

        # Query for user and verify existence
        user = User.query.filter_by(email=current_user.email).first()
        if not user:
            return "Error: user does not exist"

        # Update password
        user.pw_hash = encrypt(password, user.salt)
        user.force_pw_update = False

        # Commit changes to database
        db.session.commit()

        # Flash confirmation message and return to index
        flash("Password changed successfully", 'message')
        return redirect(url_for('index'))

@app.route('/grants-pack/<grants_pack>/budget', methods=['GET','POST'])
@login_required
@admin_required
def grants_pack_budget(grants_pack):
    """ Allows the editing of the budget for a specific grants pack """

    # Ensure grants_pack was provided
    if not grants_pack:
        return "Grants pack not specified"

    # Query for grants pack and ensure existence
    grants_week = Grants_Week.query.filter_by(grant_week=grants_pack).first()
    if not grants_week:
        return "Grants Pack does not exist"

    # Ensure grants pack has not been finalized
    if grants_week.grants_pack_finalized or grants_week.allocated:
        return "Cannot edit budget for finalized grant"

    # User is requesting form
    if request.method == 'GET':
        return render_template('grants_pack_budget.html', grants_pack=grants_week)

    # User is submitting form data
    else:

        # Get budget from form data and verify existence
        budget = request.form.get('budget')
        if not budget:
            flash("Budget not specified", "error")
            return render_template('grants_pack_budget.html', grants_pack=grants_week)

        # Verify budget in correct format
        if not isfloat(budget):
            flash("Budget format not valid", "error")
            return render_template('grants_pack_budget.html', grants_pack=grants_week)

        # Edit DB value and commit
        grants_week.budget = budget
        db.session.commit()

        # return user to grant packs page
        return redirect(url_for('grants_packs'))

@app.route('/settings/council-semester', methods=['POST'])
@login_required
@admin_required
def edit_council_semester():
    """ Provides an endpoint which allows admins to update
        the council semester via the settings page """

    # Get value from form and verify
    council_semester = request.form.get('council_semester')
    if not council_semester:
        flash("Council Semester not supplied", "error")
        return redirect(url_for(settings))
    if not match("\d{2}(F|S)", council_semester):
        flash("Invalid Council Semester Format", "error")
        return redirect(url_for(settings))

    # Update value in DB
    council_semester_db = Config.query.filter_by(key="council_semester").first()
    if not council_semester_db:
        return "Error: council semester not defined in config database"
    council_semester_db.value = council_semester

    # Get the next uncreated grants_week in the semester
    grant_week = 1
    while Grants_Week.query.filter_by(grant_week=(council_semester + '-' + str(grant_week))).first() != None:
        grant_week += 1

    # Create new grant week and add it to the DB
    grant_pack = Grants_Week(council_semester + '-' + str(grant_week))
    db.session.add(grant_pack)

    # Update Grant Week in Config DB
    grant_week_db = Config.query.filter_by(key="grant_week").first()
    if not grant_week_db:
        return "Error: grant_week not defined in Config database"
    grant_week_db.value = grant_week

    # Commit all changes to DB
    db.session.commit()

    # Display message to user and send to settings page
    flash("Council Semester has been updated successfully. A new grants pack was created.")
    return redirect(url_for('settings'))

@app.route('/treasurer/upfront/<grant_id>', methods=['GET','POST'])
@login_required
@admin_required
def upfront_payment(grant_id):
    """ A page for the treasurer to issue upfront payments to approved grants """

    # Validate Grant ID
    if not grant_id:
        return "Error: No Grant ID"
    # Query for the relevant grant
    grant = Grant.query.filter_by(grant_id=grant_id).first()
    # Return error without updating data if grant does not exist
    if grant == None:
        return "Invalid Grant ID"

    if grant.is_paid:
        return "This grant is not eligible for Treasurer review -- it has already been paid"

    # Query for the organization information and validate
    organization = Organization.query.filter_by(name=grant.organization).first()
    if not organization:
        return "Internal Error: Organization not listed in database"

    # User is requesting page
    if request.method == 'GET':
        return render_template("upfront_payment.html", grant=grant, organization=organization)

    # User is submitting form data
    else:
        # Verify the request is comming from the form
        if not request.form.get('paid') == "True":
            return "Page must be accessed via form."

        # Get and verify the amount
        amount = request.form.get('amount')
        if not amount:
            return "Amount Not Specified"

        # Update bank name if supplied
        if request.form.get('bank_name'):
            organization.bank_name = request.form.get('bank_name')

        # Update grant record with payment
        grant.is_paid = True
        grant.pay_date = datetime.now(utc)
        if not isfloat(amount):
            return "Invalid amount value"
        grant.amount_dispensed = float(amount)

        # Get check vs direct deposit info
        if request.form.get('is_check'):
            grant.is_direct_deposit = False
            grant.check_number = request.form.get('check_number')

            # Send notification email to user to pickup check
            email_check(grant)

        else:
            grant.is_direct_deposit = True

            # Send notification email to user that direct deposit occurred
            email_direct_deposit(grant)

        db.session.commit()

        # Generate Flashed Success Message
        flash('\'' + grant.project + '\' Funds Dispensed Successfully', 'success')

        return redirect(url_for('review_receipts'))

@app.route('/treasurer/upfront-review/<grant_id>', methods=['GET','POST'])
@login_required
@admin_required
def upfront_review(grant_id):
    """ A page for the treasurer to verify receipts from upfront grants """

    # Validate Grant ID
    if not grant_id:
        return "Error: No Grant ID"
    # Query for the relevant grant
    grant = Grant.query.filter_by(grant_id=grant_id).first()
    # Return error without updating data if grant does not exist
    if grant == None:
        return "Invalid Grant ID"

    if grant.receipts_reviewed:
        return "This grant is not eligible to be reviewed by the Treasurer -- it has already been reviewed"

    # User is requesting page
    if request.method == 'GET':
        receipts = grant.receipt_images.split(", ") if grant else None
        cut = (100 - grant.percentage_cut) / 100
        return render_template('upfront_receipts.html', grant=grant, receipts=receipts, cut=cut)

    # User is submitting form data
    else:

        # Get and validate amount owed
        amount_owed = request.form.get("amount_owed")
        if amount_owed == None:
            return "Amount Owed not specified"
        if not isfloat(amount_owed):
            return "Invalid amount_owed value"
        amount_owed = float(amount_owed)

        # Update the grant record
        grant.receipts_reviewed = True
        grant.receipts_reviewer = current_user.first_name + " " + current_user.last_name
        grant.treasurer_notes = request.form.get('treasurer_notes')

        if amount_owed == 0:
            grant.amount_spent = grant.amount_dispensed
            grant.must_reimburse_uc = False
        else:
            grant.amount_spent = grant.amount_dispensed - amount_owed
            grant.must_reimburse_uc = True
            grant.reimburse_uc_amount = amount_owed

        # Commit changes to database
        db.session.commit()

        # Send an email about the grant status to applicant
        email_receipts_reviewed(grant)

        # flash message to user
        flash("\'" + grant.project + "\' Receipts Successfully Reviewed", 'success')

        # Return user to treasurer page
        return redirect(url_for('review_receipts'))

@app.route('/schedule', methods=['GET','POST'])
@login_required
@admin_required
def schedule_interviews():
    """ A page for the admins to schedule interviews for the coming week """

    # User is requesting form
    if request.method == 'GET':

        # Query for interview-eligible grants
        grants = Grant.query.filter_by(interview_occurred=False,is_small_grant=False).all()

        # Render template to user
        return render_template("schedule_interviews.html", grants=grants)

    # User is submitting form data
    else:

        # Timezones will be converted to UTC
        eastern = timezone('US/Eastern')
        date_str = request.form.get('date')
        if not date_str:
            return "No Date Specified"
        date = eastern.localize(datetime.strptime(date_str, '%Y-%m-%d'))
        # Loop through all arguments looking for intervie times
        for (name,value) in request.form.items():
            # If we have found grant info, update interview time
            if name.startswith("grant:") and value:
                grant_id = name.split("grant:")[1]
                grant = Grant.query.filter_by(grant_id=grant_id).first()
                if not grant:
                    return "Invalid Grant_ID Submitted"
                hours = int(value.split(":")[0])
                minutes = int(value.split(":")[1])
                # Save interview history if necessary
                if grant.interview_schedule_date:
                    if grant.interview_schedule_history:
                        grant.interview_schedule_history += ", " + grant.interview_schedule_date.strftime("%d/%m/%Y %H:%M")
                    else:
                        grant.interview_schedule_history = grant.interview_schedule_date.strftime("%d/%m/%Y %H:%M")
                grant.interview_schedule_date = date.replace(hour=hours, minute=minutes).astimezone(utc)
                # Send email for grant interview time
                email_interview_scheduled(grant)

        db.session.commit()

        flash("Interviews Scheduled Successfully", 'message')

        return redirect(url_for('interviews'))

@app.route('/apply')
def apply():
    return redirect('https://harvard.az1.qualtrics.com/jfe1/form/SV_bQlbCpGGFSulLVP')

@app.route('/receipts-reminder', methods=['GET','POST'])
@login_required
@admin_required
def receipts_reminder():
    # User is requesting form
    if request.method == 'GET':
        return render_template('receipts_reminder.html')
    # User is submitting form
    else:
        grants = Grant.query.filter(AND(AND(Grant.receipts_submitted==False,Grant.council_approved==True), Grant.amount_allocated>0)).all()
        for grant in grants:
            email_submit_receipts(grant)
        return "Emails sent"

@app.route('/owed-money')
@login_required
@admin_required
def owed_money():
    # Query for relevant grants
    no_receipts = Grant.query.filter(AND(AND(AND(AND(AND(AND(Grant.council_approved==True,Grant.amount_allocated>0),Grant.receipts_submitted==False), Grant.receipts_due < datetime.now()), Grant.amount_dispensed>0), Grant.reimbursed_uc==False, OR(OR(Grant.hearing_requested==False,Grant.hearing_requested==None),Grant.hearing_occurred==True)))).all()
    unspent_money = Grant.query.filter(AND(AND(AND(AND(Grant.council_approved==True,Grant.amount_allocated>0),Grant.must_reimburse_uc==True),Grant.reimbursed_uc==False, OR(OR(Grant.hearing_requested==False,Grant.hearing_requested==None),Grant.hearing_occurred==True)))).all()
    # Sum owed money
    total = 0
    for grant in no_receipts:
        if grant.amount_dispensed:
            total += grant.amount_dispensed
    for grant in unspent_money:
        if grant.reimburse_uc_amount:
            total += grant.reimburse_uc_amount
    # Render page to user
    return render_template('owed_money.html', no_receipts=no_receipts, unspent_money=unspent_money, total=total)

@app.route('/owed-money/<grant_id>', methods=['GET','POST'])
@login_required
@treasurer_required
def process_owed_money(grant_id):
    # Query for grant
    grant = Grant.query.filter_by(grant_id=grant_id).first()
    if not grant:
        flash("Grant does not exist", 'error')
        return redirect(url_for('owed_money'))
    # User is requesting form
    if request.method == 'GET':
        return render_template('process_owed_money.html', grant=grant)
    # User is submitting form
    else:
        # Update DB
        grant.reimbursed_uc = True
        if request.form.get("reimbursement_amount"):
            grant.reimburse_uc_amount = request.form.get("reimbursement_amount")
        db.session.commit()
        # Send Email
        email_reimbursement_complete(grant)
        # Notify Admin
        flash("Successfully Processed Owed Money for " + grant.project, 'success')
        return redirect(url_for('owed_money'))

@app.route('/grant/<grant_id>/raw', methods=['GET','POST'])
@login_required
@treasurer_required
def raw_grant_edit(grant_id):
    GrantForm = model_form(Grant, Form)
    grant = Grant.query.filter_by(grant_id=grant_id).first()
    if not grant:
        flash("Grant does not exist", 'error')
        return redirect(url_for('index'))
    # User is requesting form
    if request.method == 'POST':
        form = GrantForm(request.form)
        for field in form:
            if field.type == "DateTimeField":
                if request.form.get(field.name) != '' and request.form.get(field.name) != None:
                    setattr(grant, field.name, datetime.strptime(request.form[field.name], "%Y-%m-%dT%H:%M"))
            elif field.data == "":
                setattr(grant, field.name, None)
            else:
                setattr(grant, field.name, field.data)
        db.session.commit()
        flash("Grant " + grant.grant_id + " updated successfully.", 'success')
        return redirect(url_for('raw_grant_edit', grant_id=grant.grant_id))
    # User is submitting form
    else:
        form = GrantForm(obj=grant)
        return render_template("raw_grant_edit.html", form=form, grant=grant)

@app.route('/send-owe-emails')
@login_required
@admin_required
def send_owe():
    """ A manual way to invoke the every-other day send owed money emails. Does not
        modify two day timer """
    send_owe_money_emails()
    flash("Send Owed Money emails sent.", 'success')
    return redirect(url_for('index'))

@app.route('/grant/<grant_id>/receipts')
def view_receipts(grant_id):
    """ Displays receipts for specified grant in read-only format """
    # Ensure that grant_id was specified
    if not grant_id:
        return "Must specify grant id."
    # Query for grant
    grant = Grant.query.filter_by(grant_id=grant_id).first()
    # Ensure that grant exists
    if not grant:
        return "Grant " + grant_id + " does not exist."
    # Get the list of receipts
    receipts = grant.receipt_images
    if receipts:
        receipts = receipts.split(", ")
    # Render the page to the user
    return render_template("grant_receipts.html", grant=grant, receipts=receipts)

@app.route('/hearings')
@login_required
@admin_required
def hearings():
    """ An interface to view and schedule all pending hearings """
    grants = Grant.query.filter(AND(Grant.hearing_requested==True,OR(Grant.hearing_occurred==False,Grant.hearing_occurred==None))).all()
    return render_template("hearings.html", grants=grants)

@app.route('/request-hearing', methods=['POST'])
@login_required
@admin_required
def request_hearing():
    """ Requests a hearing for a given grant """
    grant_id = request.form.get("grant_id")
    # Ensure that grant_id was specified
    if not grant_id:
        return "Must specify grant id."
    # Query for grant
    grant = Grant.query.filter_by(grant_id=grant_id).first()
    # Ensure that grant exists
    if not grant:
        return "Grant " + grant_id + " does not exist."
    # Update Grant
    grant.hearing_requested = True
    db.session.commit()
    flash("Hearing successfully requested for \"" + grant.project + "\".", 'success')
    return redirect(url_for('hearings'))

@app.route('/expenses')
def expenses():
    """ Lists all expenses in the current council's budget """
    council_semester = Config.query.filter_by(key="council_semester").first()
    council = council_semester.value[:2] if council_semester else None
    funds = Fund.query.filter_by(council=council).all()
    return render_template("expenses.html", funds=funds)

@app.route('/expenses/manage/add-budget', methods=['GET','POST'])
@login_required
@treasurer_required
def add_budget():
    """ Adds a new budget to the system """
    # User is requesting form
    if request.method == 'GET':
        return render_template("add_budget.html")
    # User is submitting form
    else:
        if "council" not in request.form or not request.form["council"]:
            flash("Council number not provided", 'error')
            return render_template("add_budget.html")
        if "amount" not in request.form or not request.form["amount"]:
            flash("Budget amount not provided", 'error')
            return render_template("add_budget.html")
        # check if the post request has the file part
        if 'budget' not in request.files:
            flash('No file part', 'error')
            return redirect(url_for("add_budget"))
        file = request.files['budget']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(url_for("add_budget"))
        if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() == 'pdf':
            filename = secure_filename(strftime("%m%d%Y-%H%M%S_") + file.filename)
            file.save(join(app.config['UPLOAD_FOLDER'], filename))
            # Create DB object for new budget
            budget = Budget(request.form["council"])
            budget.amount = request.form["amount"]
            budget.file = filename
            db.session.add(budget)
            db.session.commit()
            flash("Budget Successfully Added", 'success')
            return render_template("add_budget.html")
        else:
            flash("Budget must be a PDF", 'error')
            return redirect(url_for("add_budget"))

@app.route('/budget/<council>')
def council_budget(council):
    """ Supplies the budget PDF file for a given council """
    budget = Budget.query.filter_by(council=council).first()
    if not budget:
        flash("Budget does not exist", 'error')
        return redirect(url_for("index"))
    return send_from_directory(app.config['UPLOAD_FOLDER'], budget.file)

@app.route('/budget')
def budget():
    """ Supplies the budget PDF file for the current given council """
    council = db.session.query(db.func.max(Budget.council)).scalar()
    return council_budget(council)

@app.route('/expenses/manage')
@login_required
@treasurer_required
def manage_expenses():
    """ A dashboard of links for managing full-council expenses """
    return render_template("manage_expenses.html")

@app.route('/expenses/manage/add-expense', methods=['GET','POST'])
@login_required
@treasurer_required
def add_expense():
    """ Adds an expense to the system """
    # User is requesting form
    if request.method == 'GET':
        council = db.session.query(db.func.max(Budget.council)).scalar()
        funds = Fund.query.filter_by(council=council).all()
        return render_template('add_expense.html', funds=funds)
    # User is submitting form
    else:
        if "name" not in request.form or not request.form["name"]:
            flash("Expense name not provided", 'error')
            return render_template("add_budget.html")
        if "amount" not in request.form or not request.form["amount"]:
            flash("Expense budgeted amount not provided", 'error')
            return render_template("add_budget.html")
        if "fund" not in request.form or not request.form["fund"]:
            flash("Fund not selected", 'error')
            return render_template("add_budget.html")
        filename = None
        if "legislation" in request.files:
            file = request.files['legislation']
            if file.filename:
                if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() == 'pdf':
                    filename = secure_filename(strftime("%m%d%Y-%H%M%S_") + file.filename)
                    file.save(join(app.config['UPLOAD_FOLDER'], filename))
                else:
                    flash("Budget must be a PDF", 'error')
                    return redirect(url_for("add_budget"))
        fund = Fund.query.get(request.form["fund"])
        if not fund:
            flash("Fund does not exist", 'error')
        expense = Expense(request.form["name"], fund, request.form["amount"])
        expense.legislation_file = filename
        expense.legislation_number = request.form.get("leg_num")
        db.session.add(expense)
        db.session.commit()
        flash("Expense " + request.form["name"] + " Added Successfully", 'success')
        return redirect(url_for("manage_expenses"))

@app.route('/expenses/manage/add-fund', methods=['GET','POST'])
@login_required
@treasurer_required
def add_fund():
    """ Adds a fund to the system """
    # User is requesting form
    if request.method == 'GET':
        return render_template("add_fund.html")
    # User is submitting form
    else:
        if not request.form.get("name"):
            flash("Fund name not provided", 'error')
            return render_template("add_fund.html")
        if not request.form.get("amount"):
            flash("Fund amount not provided", 'error')
            return render_template("add_fund.html")
        # Check that the fund doesn't already exist
        council = db.session.query(db.func.max(Budget.council)).scalar()
        dup = Fund.query.filter_by(council=council, name=request.form["name"]).first()
        if dup:
            flash("Fund already exists", 'error')
            return render_template("add_fund.html")
        fund = Fund(request.form["name"],request.form["amount"])
        fund.council = council
        db.session.add(fund)
        db.session.commit()
        flash("Fund " + request.form["name"] + " Added Successfully", 'success')
        return redirect(url_for("manage_expenses"))

@app.route('/expenses/<id>')
def expense_legislation(id):
    """ Serves a requested legislation pdf for a given expense """
    expense = Expense.query.get(id)
    if not expense:
        flash("Expense does not exist", 'error')
        return redirect(url_for("index"))
    if not expense.legislation_file:
        flash("Expense does not have attached legislation", 'error')
        return redirect(url_for("index"))
    return send_from_directory(app.config['UPLOAD_FOLDER'], expense.legislation_file)

@app.route('/export', methods=['GET','POST'])
@login_required
def export():
    """ Export all Grants data as CSV """
    fields = sorted(list(model_fields(Grant).keys()))
    def generate():
        # Write header
        yield ','.join(fields) + '\n'
        for grant in Grant.query.all():
            for field in fields:
                val = '\"' + str(getattr(grant,field)).replace('\n', ' ').replace('\r', '').replace('\"', '\"\"') + '\"' if getattr(grant,field) is not None else ""
                yield val + ','
            yield '\n'
    return Response(stream_with_context(generate()), mimetype='text/csv')

@app.route('/expenses/<id>/edit', methods=['GET','POST'])
@login_required
@treasurer_required
def expense_edit(id):
    """ Allows editing spent amount of existing expenses """
    expense = Expense.query.get(id)
    if not expense:
        flash("Expense does not exist", 'error')
        return redirect(url_for("index"))
    if request.method == 'GET':
        # Serve the form
        return render_template('expenses_edit.html', expense=expense)
    else:
        # Handle the form submitted data
        if request.form['spent']:
            # Update the DB
            expense.spent = request.form['spent']
            db.session.commit()
            # Notify the user
            flash("Expense updated successfully.", 'success')
            return redirect(url_for('expenses'))
        else:
            # Form submission missing required data
            flash("Error: Request missing required form data.", 'error')
            return render_template('expenses_edit', expense=expense)

@app.route('/expenses/<id>/delete', methods=['GET','POST'])
@login_required
@treasurer_required
def expense_delete(id):
    """ Deletes the supplied expense record """
    # Query for the expense
    expense = Expense.query.get(id)
    if not expense:
        flash("Expense does not exist", 'error')
        return redirect(url_for("index"))
    # Serve the form
    if request.method == 'GET':
        return render_template('expense_delete.html', expense=expense)
    # Handle form submission
    else:
        # Remove the expense from the DB
        db.session.delete(expense)
        db.session.commit()
        # Notify the user
        flash("Expense deleted successfully.", 'success')
        return redirect(url_for('expenses'))
