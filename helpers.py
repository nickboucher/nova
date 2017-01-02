#
# helpers.py
# Nicholas Boucher 2017
#
# Contains a set of general functions that assist the main 
# application in data-processing
#

from database_models import *
from urllib.parse import parse_qs
from pytz import timezone, utc

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
