#
# helpers.py
# Nicholas Boucher 2017
#
# Contains a set of general functions that assist the main
# application in data-processing. Also contain the login
# class.
#

from urllib.parse import parse_qs
from pytz import timezone, utc
from flask_login import LoginManager, current_user, login_required
from flask import flash, redirect, url_for, render_template
from hashlib import pbkdf2_hmac
from binascii import hexlify
from functools import wraps
from os import urandom
from flask_mail import Message
from sys import argv
from threading import Thread
from collections import namedtuple
from queue import Queue
from datetime import datetime, timedelta
from sqlalchemy.sql.expression import or_ as OR, and_ as AND
from database_models import *

# Avoid import errors for installation script
if "installation" not in argv[0]:
    import application

def usd(value):
    """ Formats value as USD. """
    if value == None:
        return ""
    return "${:,.2f}".format(value)

def two_decimals(value):
    """ Formats float to 2 decimal string """
    if value == None:
        return ""
    return "{:.2f}".format(value)

def number(value):
    """ Formats float to 2 decimal string with no commas """
    if value == None:
        return ""
    return "{:.2f}".format(value)

def suppress_none(value):
    """ Returns value or empty string if None """

    if value == None:
        return ""
    return value

def utc_to_east_datetime(utc_dt):
    """ Formats datetime as US Eastern timezone """
    if utc_dt == None:
        return ""
    eastern = timezone('US/Eastern')
    return utc_dt.replace(tzinfo=utc).astimezone(tz=eastern).strftime("%B %-d, %Y %-I:%M %p")

def utc_to_east_date(utc_dt):
    """ Formats date in US Eastern timezone """
    if utc_dt == None:
        return ""
    eastern = timezone('US/Eastern')
    return utc_dt.replace(tzinfo=utc).astimezone(tz=eastern).strftime("%B %-d, %Y")

def nfloat(s):
    """ Returns the float equivalent of a string, or 'None' if not possible """
    try:
        return float(s)
    except ValueError:
        return None

def percentage(value):
    """ Returns a rounded, expanded percentage from a float in [0,1] """
    return round(value * 100, 2)

def get_grant_args(query_string):
    """ Gets arguments specific to application from query string,
        escaping some troublsesome characters """

    # Escape all ampersands in query string that don't seem relevant
    # (Unfortunately, Qualtrisc doesn't do this for us)
    raw_data = query_string.decode('utf8').split('&')
    # tuple of valid query keys (adding 'k' for security key)
    grant_fields = list(vars(Grant).keys())
    grant_fields.append('k')
    valid_queries = tuple(grant_fields)
    parsed_args = []
    for arg in raw_data:
        # Skip first param, check if if arg starts with acceptable field
        if len(parsed_args) == 0 or arg.startswith(valid_queries):
            # add argument to list and escapse ';', '+', and '#'
            parsed_args.append(arg.replace(';','%3B').replace('+','%2B').replace('#','%23'))
        else:
            # append argument to previous arg and escapse '&', ';', '+', and '#'
            parsed_args[-1] += "%26" + arg.replace(';','%3B').replace('+','%2B').replace('#','%23')
    # Rebuild query string and parse as if normal
    clean_query = "&".join(parsed_args)
    return parse_qs(clean_query)

def serialize_grant(grant):
    """ Turns grant object into a dictionary that can be easily JSONified for API calls """
    return {
            'grant_id' : grant.grant_id,
            'organization' : grant.organization,
            'project' : grant.project,
            'grants_pack' : grant.grants_pack,
            'interview_or_review_occurred' : grant.small_grant_is_reviewed if grant.is_small_grant else grant.interview_occurred,
            'cpf_submitted' : grant.receipts_submitted,
            'funds_dispensed' : grant.is_paid
        }

def serialize_grant_full(grant):
    """ Serializes every data member in the grant object to a dictionary for multithreading """

    # create empty dict
    _grant = {}

    # Populate with data
    for c in Grant.__table__.columns:
        _grant[c.name] = getattr(grant, c.name)

    # return populated dict
    return _grant

def encrypt(password, salt):
    """ Provides a default implementation of the encryption algorithm used by nova """
    return hexlify(pbkdf2_hmac('sha256', str.encode(password), str.encode(salt), 100000)).decode('utf-8')

def verify_password(user, password):
    """ Checks whether the password is correct for a given user """
    return user.pw_hash == encrypt(password, user.salt)

def create_user(email, first_name, last_name, password, admin):
    """ Handy function to create a new user """

    # Generate a random 32-byte salt
    salt = hexlify(urandom(32)).decode('utf-8')
    # Hash the password
    pw_hash = encrypt(password, salt)

    # Create the new User object
    return User(email, first_name, last_name, admin, pw_hash, salt)

def admin_required(func):
    """ Requires admin priveleges on page. Should wrap with
        @login_required above this wrapper """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.admin:
            flash("You must be an adminstrator to access this page.", "message")
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    return decorated_view

def isfloat(value):
    """ Simple function that return a Boolean representing whether
        the input string was in valid float form """
    try:
        float(value)
    except ValueError:
        return False
    return True

class DictObj(object):
    """ Simple class which will let us create object from dict """
    def __init__(self, d):
        self.__dict__ = d

# We want to send email in the background, but sending multiple
# simultaneously causes problems with Google's SMPTP server.
# As such, we will use a single background worker thread with
# a thread-safe queue to handle sneding emails.
q = Queue()
def worker():
    while True:
        (func,grant) = q.get()
        func(grant)
        q.task_done()
thr = Thread(target=worker)
thr.daemon = True
thr.start()

def async_grant(func):
    """ Runs function on separate thread with a dictionary-serialized-object version
        of the grant argument to eliminate SQL-Alchemy multithreading issues.
        Should wrap like: @async_grants """
    def inner_wrapper(_grant):
        # Retrieve app context in separate thread
        with application.app.app_context():
            func(_grant)
    def wrapper(grant):
        _grant = DictObj(serialize_grant_full(grant))
        q.put((inner_wrapper,_grant))
    return wrapper

def if_email(func):
    """ Simple wrapper to only run function if the email_enabled Config
        option is set to True """
    def wrapper(grant):
        email = Config.query.filter_by(key='enable_email').first()
        if email.value == '1':
            func(grant)
    return wrapper

@if_email
@async_grant
def email_application_submitted(grant):
    """ Sends an application submitted confirmation email to the grant applicant """

    # Create Message
    msg = Message("Grant Application Submitted", recipients=[grant.contact_email])

    # Define attached image
    image = "submitted.gif"

    # Attach HTML Body
    html = render_template("email/grant_submit.html", grant=grant, image=image)
    msg.html = html

    # Attach Image
    with application.app.open_resource("templates/email/images/%s" % image) as fp:
        msg.attach(image, "image/gif", fp.read(), headers=[['Content-ID', '<%s>' % image],])

    # Send Email
    application.mail.send(msg)

@if_email
@async_grant
def email_application_passed(grant):
    """ Sends an email to the grant applicant stating the grant has passed the council
        and requesting receipts """

    # Create Message
    msg = Message("Grant Application Passed", recipients=[grant.contact_email])

    # Define attached image
    image = "receipts.gif"

    # Attach HTML Body
    html = render_template("email/grant_passed.html", grant=grant, image=image)
    msg.html = html

    # Attach Image
    with application.app.open_resource("templates/email/images/%s" % image) as fp:
        msg.attach(image, "image/gif", fp.read(), headers=[['Content-ID', '<%s>' % image],])

    # Send Email
    application.mail.send(msg)

@if_email
@async_grant
def email_application_denied(grant):
    """ Sends an email to the grant applicant stating the grant has been denied
        by the council """

    # Create Message
    msg = Message("Grant Application Denied", recipients=[grant.contact_email])

    # Define attached image
    image = "denied.gif"

    # Attach HTML Body
    html = render_template("email/grant_denied.html", grant=grant, image=image)
    msg.html = html

    # Attach Image
    with application.app.open_resource("templates/email/images/%s" % image) as fp:
        msg.attach(image, "image/gif", fp.read(), headers=[['Content-ID', '<%s>' % image],])

    # Send Email
    application.mail.send(msg)

@if_email
@async_grant
def email_interview_scheduled(grant):
    """ Sends an email to the grant applicant stating the interview for the grant
        has been scheduled """

    # Create Message
    msg = Message("Grant Interview Scheduled", recipients=[grant.contact_email])

    # Define attached image
    image = "scheduled.gif"

    # Attach HTML Body
    html = render_template("email/interview_scheduled.html", grant=grant, image=image)
    msg.html = html

    # Attach Image
    with application.app.open_resource("templates/email/images/%s" % image) as fp:
        msg.attach(image, "image/gif", fp.read(), headers=[['Content-ID', '<%s>' % image],])

    # Send Email
    application.mail.send(msg)

@if_email
@async_grant
def email_interview_completed(grant):
    """ Sends an email to the grant applicant stating the interview for the grant
        has been completed """

    # Create Message
    msg = Message("Grant Interview Completed", recipients=[grant.contact_email])

    # Define attached image
    image = "interviewed.gif"

    # Attach HTML Body
    html = render_template("email/interview_complete.html", grant=grant, image=image)
    msg.html = html

    # Attach Image
    with application.app.open_resource("templates/email/images/%s" % image) as fp:
        msg.attach(image, "image/gif", fp.read(), headers=[['Content-ID', '<%s>' % image],])

    # Send Email
    application.mail.send(msg)

@if_email
@async_grant
def email_direct_deposit(grant):
    """ Sends an email to the grant applicant stating the funds have been direct deposited
        into their bank account """

    # Create Message
    msg = Message("Grant Funds Deposited", recipients=[grant.contact_email], sender=("UC Treasurer", "harvarductreasurer@gmail.com"))

    # Define attached image
    image = "deposited.gif"

    # Attach HTML Body
    html = render_template("email/direct_deposit.html", grant=grant, image=image)
    msg.html = html

    # Attach Image
    with application.app.open_resource("templates/email/images/%s" % image) as fp:
        msg.attach(image, "image/gif", fp.read(), headers=[['Content-ID', '<%s>' % image],])

    # Send Email
    application.treasurer_mail.send(msg)

@if_email
@async_grant
def email_receipts_submitted(grant):
    """ Sends an email to the grant applicant stating the the receipts have been
        submitted """

    # Create Message
    msg = Message("Grant Receipts Submitted", recipients=[grant.contact_email])

    # Define attached image
    image = "receipts_submitted.gif"

    # Attach HTML Body
    html = render_template("email/receipts_submitted.html", grant=grant, image=image)
    msg.html = html

    # Attach Image
    with application.app.open_resource("templates/email/images/%s" % image) as fp:
        msg.attach(image, "image/gif", fp.read(), headers=[['Content-ID', '<%s>' % image],])

    # Send Email
    application.mail.send(msg)

@if_email
@async_grant
def email_check(grant):
    """ Sends an email to the grant applicant stating the a check is ready to be picked
        up for their grant """

    # Create Message
    msg = Message("Grant Check Ready", recipients=[grant.contact_email], sender=("UC Treasurer", "harvarductreasurer@gmail.com"))

    # Define attached image
    image = "check.gif"

    # Attach HTML Body
    html = render_template("email/check.html", grant=grant, image=image)
    msg.html = html

    # Attach Image
    with application.app.open_resource("templates/email/images/%s" % image) as fp:
        msg.attach(image, "image/gif", fp.read(), headers=[['Content-ID', '<%s>' % image],])

    # Send Email
    application.treasurer_mail.send(msg)

@if_email
@async_grant
def email_receipts_reviewed(grant):
    """ Sends an email to the grant applicant stating the their receipts have been reviewed
        and approved/owe money """

    # Define subject and image
    if grant.must_reimburse_uc and not grant.reimbursed_uc:
        subject = "Owed Money on Grant"
        image = "owe.gif"
        grant.owed_money_email_date = datetime.now()
        db.session.commit()
    else:
        subject = "Grant Receipts Reviewed"
        image = "done.gif"

    # Create Message
    msg = Message(subject, recipients=[grant.contact_email], sender=("UC Treasurer", "harvarductreasurer@gmail.com"))

    # Attach HTML Body
    html = render_template("email/receipts_reviewed.html", grant=grant, image=image)
    msg.html = html

    # Attach Image
    with application.app.open_resource("templates/email/images/%s" % image) as fp:
        msg.attach(image, "image/gif", fp.read(), headers=[['Content-ID', '<%s>' % image],])

    # Send Email
    application.treasurer_mail.send(msg)

@if_email
@async_grant
def email_submit_receipts(grant):
    """ Sends a reminder email to the grant applicant to submit receipts """

    # Create Message
    msg = Message("Submit Receipts", recipients=[grant.contact_email])

    # Define attached image
    image = "receipts.gif"

    # Attach HTML Body
    html = render_template("email/submit_receipts.html", grant=grant, image=image)
    msg.html = html

    # Attach Image
    with application.app.open_resource("templates/email/images/%s" % image) as fp:
        msg.attach(image, "image/gif", fp.read(), headers=[['Content-ID', '<%s>' % image],])

    # Send Email
    application.mail.send(msg)

@if_email
@async_grant
def email_receipts_not_submitted(grant):
    """ Sends an email to the grant applicant letting them know that they did not submit receipts
        before the deadline """
    print("Not Submitted: " + grant.grant_id)
    # Create Message
    msg = Message("Receipts Deadline Passed", recipients=[grant.contact_email])

    # Define attached image
    if grant.is_upfront:
        image = "owe.gif"
    else:
        image = "denied.gif"

    # Attach HTML Body
    html = render_template("email/submit_receipts.html", grant=grant, image=image)
    msg.html = html

    # Attach Image
    with application.app.open_resource("templates/email/images/%s" % image) as fp:
        msg.attach(image, "image/gif", fp.read(), headers=[['Content-ID', '<%s>' % image],])

    # Send Email
    application.mail.send(msg)

@if_email
@async_grant
def email_owed_money(grant):
    """ Send an email to the grant applicant reminding them that they owe money """
    print("Owed: " + grant.grant_id)
    return
    # Create Message
    msg = Message("Owed Money Reminder", recipients=[grant.contact_email], sender=("UC Treasurer", "harvarductreasurer@gmail.com"))

    # Define attached image
    image = "owe.gif"

    # Attach HTML Body
    html = render_template("email/owed_money_notice.html", grant=grant, image=image)
    msg.html = html

    # Attach Image
    with application.app.open_resource("templates/email/images/%s" % image) as fp:
        msg.attach(image, "image/gif", fp.read(), headers=[['Content-ID', '<%s>' % image],])

    # Send Email
    application.treasurer_mail.send(msg)

@if_email
@async_grant
def email_reimbursement_complete(grant):
    """ Send an email to the grant applicant notifying them that the grant UC reimbursement process is complete """

    # Create Message
    msg = Message("Grant Process Complete", recipients=[grant.contact_email], sender=("UC Treasurer", "harvarductreasurer@gmail.com"))

    # Define attached image
    image = "done.gif"

    # Attach HTML Body
    html = render_template("email/reimbursement_complete.html", grant=grant, image=image)
    msg.html = html

    # Attach Image
    with application.app.open_resource("templates/email/images/%s" % image) as fp:
        msg.attach(image, "image/gif", fp.read(), headers=[['Content-ID', '<%s>' % image],])

    # Send Email
    application.treasurer_mail.send(msg)

def send_owe_money_emails():
    """ Sends emails to all groups that owe money to the UC reminding them to pay """
    # Don't bug people if we bugged them within past 2 days
    print("Sending Emails")
    now = datetime.now()
    two_days_ago = now - timedelta(days=2)
    with application.app.app_context():
        # Query for no receipts grants
        no_receipts = Grant.query.filter(AND(AND(AND(AND(AND(Grant.council_approved==True,Grant.amount_allocated>0),Grant.receipts_submitted==False), Grant.receipts_due < now), Grant.amount_dispensed>0), Grant.reimbursed_uc==False)).all()
        for grant in no_receipts:
            print(grant.grant_id)
            if grant.owed_money_email_date and grant.owed_money_email_date < two_days_ago:
                email_owed_money(grant)
            elif not grant.owed_money_email_date:
                email_receipts_not_submitted(grant)
                grant.owed_money_email_date = now
        # Query for grants that didn't spend all money
        unspent_money = Grant.query.filter(AND(AND(AND(Grant.council_approved==True,Grant.amount_allocated>0),Grant.must_reimburse_uc==True),Grant.reimbursed_uc==False)).all()
        for grant in unspent_money:
            print(grant.grant_id)
            if not grant.owed_money_email_date or grant.owed_money_email_date < two_days_ago:
                email_owed_money(grant)
                if not grant.owed_money_email_date:
                    grant.owed_money_email_date = now
        db.session.commit()
