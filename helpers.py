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
from flask import current_app
from hashlib import pbkdf2_hmac
from binascii import hexlify
from functools import wraps
from os import urandom
from database_models import *

def usd(value):
    """ Formats value as USD. """
    if value == None:
        return ""
    return "${:,.2f}".format(value)
    
def two_decimals(value):
    """ Formats float to 2 decimal string """
    if value == None:
        return ""
    return "{:,.2f}".format(value)
    
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
    return utc_dt.replace(tzinfo=utc).astimezone(tz=eastern).strftime("%B %-d, %Y %-I:%-M %p")
    
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
            # add argument to list and escapse ';' and '+'
            parsed_args.append(arg.replace(';','%3B').replace('+','%2B'))
        else:
            # append argument to previous arg and escapse '&', ';', and '+'
            parsed_args[-1] += "%26" + arg.replace(';','%3B').replace('+','%2B')
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
            return current_app.login_manager.unauthorized()
        return func(*args, **kwargs)
    return decorated_view