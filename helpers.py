def usd(value):
    """Formats value as USD."""
    return "${:,.2f}".format(value)
    
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
            parsed_args.append(arg)
        else:
            # append argument to previous arg and escapse '&'
            parsed_args[-1] += "%26" + arg.replace(';','%3B')
    # Rebuild query string and parse as if normal
    clean_query = "&".join(parsed_args)
    return parse_qs(clean_query)