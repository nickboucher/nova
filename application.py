from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from urllib.parse import parse_qs
from helpers import *

# create Flask server
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# custom filter
app.jinja_env.filters["usd"] = usd

#set cryptographic key for Sessions
app.secret_key = "some really good encryption string"

# setup database connection
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Database Model
class Grant(db.Model):
    # General Grant Info
    id = db.Column(db.Integer, primary_key=True)
    grant_id = db.Column(db.String(64), unique=True)
    # Application Info
    amount_requested = db.Column(db.Float)
    is_collaboration = db.Column(db.Boolean)
    collaborators = db.Column(db.Text) #comma-separated
    collaboration_explanation = db.Column(db.Text)
    contact_first_name = db.Column(db.Text)
    contact_last_name = db.Column(db.Text)
    contact_email = db.Column(db.Text)
    contact_phone = db.Column(db.Text)
    contact_role = db.Column(db.Text)
    is_upfront = db.Column(db.Boolean)
    organization = db.Column(db.Text)
    tax_id = db.Column(db.Text)
    project = db.Column(db.Text)
    project_description = db.Column(db.Text)
    is_event = db.Column(db.Boolean)
    project_location = db.Column(db.Text)
    project_start = db.Column(db.DateTime)
    project_end = db.Column(db.DateTime)
    college_attendees = db.Column(db.Integer)
    facebook_link = db.Column(db.Text)
    revenue1_type = db.Column(db.Text)
    revenue1_description = db.Column(db.Text)
    revenue1_amount = db.Column(db.Float)
    revenue2_type = db.Column(db.Text)
    revenue2_description = db.Column(db.Text)
    revenue2_amount = db.Column(db.Float)
    revenue3_type = db.Column(db.Text)
    revenue3_description = db.Column(db.Text)
    revenue3_amount = db.Column(db.Float)
    revenue4_type = db.Column(db.Text)
    revenue4_description = db.Column(db.Text)
    revenue4_amount = db.Column(db.Float)
    revenue5_type = db.Column(db.Text)
    revenue5_description = db.Column(db.Text)
    revenue5_amount = db.Column(db.Float)
    revenue6_type = db.Column(db.Text)
    revenue6_description = db.Column(db.Text)
    revenue6_amount = db.Column(db.Float)
    revenue7_type = db.Column(db.Text)
    revenue7_description = db.Column(db.Text)
    revenue7_amount = db.Column(db.Float)
    revenue8_type = db.Column(db.Text)
    revenue8_description = db.Column(db.Text)
    revenue8_amount = db.Column(db.Float)
    revenue9_type = db.Column(db.Text)
    revenue9_description = db.Column(db.Text)
    revenue9_amount = db.Column(db.Float)
    revenue10_type = db.Column(db.Text)
    revenue10_description = db.Column(db.Text)
    revenue10_amount = db.Column(db.Float)
    app_expense1_type = db.Column(db.Text)
    app_expense1_description = db.Column(db.Text)
    app_expense1_amount = db.Column(db.Float)
    app_expense2_type = db.Column(db.Text)
    app_expense2_description = db.Column(db.Text)
    app_expense2_amount = db.Column(db.Float)
    app_expense3_type = db.Column(db.Text)
    app_expense3_description = db.Column(db.Text)
    app_expense3_amount = db.Column(db.Float)
    app_expense4_type = db.Column(db.Text)
    app_expense4_description = db.Column(db.Text)
    app_expense4_amount = db.Column(db.Float)
    app_expense5_type = db.Column(db.Text)
    app_expense5_description = db.Column(db.Text)
    app_expense5_amount = db.Column(db.Float)
    app_expense6_type = db.Column(db.Text)
    app_expense6_description = db.Column(db.Text)
    app_expense6_amount = db.Column(db.Float)
    app_expense7_type = db.Column(db.Text)
    app_expense7_description = db.Column(db.Text)
    app_expense7_amount = db.Column(db.Float)
    app_expense8_type = db.Column(db.Text)
    app_expense8_description = db.Column(db.Text)
    app_expense8_amount = db.Column(db.Float)
    app_expense9_type = db.Column(db.Text)
    app_expense9_description = db.Column(db.Text)
    app_expense9_amount = db.Column(db.Float)
    app_expense10_type = db.Column(db.Text)
    app_expense10_description = db.Column(db.Text)
    app_expense10_amount = db.Column(db.Float)
    app_expense11_type = db.Column(db.Text)
    app_expense11_description = db.Column(db.Text)
    app_expense11_amount = db.Column(db.Float)
    app_expense12_type = db.Column(db.Text)
    app_expense12_description = db.Column(db.Text)
    app_expense12_amount = db.Column(db.Float)
    application_comments = db.Column(db.Text)
    # Interview Info
    interviewer = db.Column(db.Text)
    interview_date = db.Column(db.DateTime)
    interviewer_notes = db.Column(db.Text)
    food_allocated = db.Column(db.Float)
    food_allocated_notes = db.Column(db.Text)
    travel_allocated = db.Column(db.Float)
    travel_allocated_notes = db.Column(db.Text)
    publicity_allocated = db.Column(db.Float)
    publicity_allocated_notes = db.Column(db.Text)
    materials_allocated = db.Column(db.Float)
    materials_allocated_notes = db.Column(db.Text)
    food_allocated = db.Column(db.Float)
    food_allocated_notes = db.Column(db.Text)
    venue_allocated = db.Column(db.Float)
    venue_allocated_notes = db.Column(db.Text)
    decorations_allocated = db.Column(db.Float)
    decorations_allocated_notes = db.Column(db.Text)
    media_allocated = db.Column(db.Float)
    media_allocated_notes = db.Column(db.Text)
    admissions_allocated = db.Column(db.Float)
    admissions_allocated_notes = db.Column(db.Text)
    hupd_allocated = db.Column(db.Float)
    hupd_allocated_notes = db.Column(db.Text)
    personnel_allocated = db.Column(db.Float)
    personnel_allocated_notes = db.Column(db.Text)
    other_allocated = db.Column(db.Float)
    other_allocated_notes = db.Column(db.Text)
    # Completed Project Info
    expense1_description = db.Column(db.Text)
    expense1_amount = db.Column(db.Float)
    expense2_description = db.Column(db.Text)
    expense2_amount = db.Column(db.Float)
    expense3_description = db.Column(db.Text)
    expense3_amount = db.Column(db.Float)
    expense4_description = db.Column(db.Text)
    expense4_amount = db.Column(db.Float)
    expense5_description = db.Column(db.Text)
    expense5_amount = db.Column(db.Float)
    expense6_description = db.Column(db.Text)
    expense6_amount = db.Column(db.Float)
    expense7_description = db.Column(db.Text)
    expense7_amount = db.Column(db.Float)
    expense8_description = db.Column(db.Text)
    expense8_amount = db.Column(db.Float)
    expense9_description = db.Column(db.Text)
    expense9_amount = db.Column(db.Float)
    expense10_description = db.Column(db.Text)
    expense10_amount = db.Column(db.Float)
    expense11_description = db.Column(db.Text)
    expense11_amount = db.Column(db.Float)
    expense12_description = db.Column(db.Text)
    expense12_amount = db.Column(db.Float)
    receipt_images = db.Column(db.Text) # comma-separated file numbers
    completed_proj_comments = db.Column(db.Text)
    # Treasurer Info
    pay_date = db.Column(db.DateTime)
    is_direct_deposit = db.Column(db.Boolean)
    check_number = db.Column(db.String(64))
    amount_spent = db.Column(db.Float)


    def __init__(self, grant_id):
        self.grant_id = grant_id

    def __repr__(self):
        return '<Grant %r>' % self.grant_id

class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Organization %r>' % self.name
        
class Config(db.Model):
    key = db.Column(db.String(64), primary_key=True)
    value = db.Column(db.Text)

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __repr__(self):
        return '<Config %r>' % self.key
        
class Grant_Count(db.Model):
    grant_week = db.Column(db.String(64), primary_key=True)
    num_grants = db.Column(db.Integer)

    def __init__(self, grant_week):
        self.grant_week = grant_week
        self.num_grants = 0

    def __repr__(self):
        return '<Grant_Count %r>' % self.grant_week
        
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/new_grant')
def new_grant():
    """Inserts new grant applications into database from query strings passed by qualtrics survey """
    
    # Escape all ampersands in query string that don't seem relevant
    # (Unfortunately, Qualtrisc doesn't do this for us)
    raw_data = request.query_string.decode('utf8').split('&')
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
    args = parse_qs(clean_query)
    
    # Verify security key
    sec_key = Config.query.filter_by(key='security_key').first().value
    if not args.get('k') or sec_key != args.get('k')[0]:
        return "Invalid Security Key. You do not have access to this system."
    
    # Get Next Grant ID
    current_week = Config.query.filter_by(key='grant_week').first()
    grant_number = Grant_Count.query.filter_by(grant_week=current_week.value).first()
    # This is not atomic, which seems like a potential problem...
    grant_number.num_grants += 1
    db.session.commit()
    grant_id = current_week.value + "-" + str(grant_number.num_grants)
    
    # Create New Grant
    grant = Grant(grant_id)
    
    print(args)
    
    # Add Grant Values from Parsed Query String
    print(args.get('amount_requested')[0])
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
    if args.get('project_start'): grant.project_start = datetime.strptime(args.get('project_start')[0], '%m/%d/%Y')
    if args.get('project_end'): grant.project_end = datetime.strptime(args.get('project_end')[0], '%m/%d/%Y')
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
    
    try:
        db.session.add(grant)
        db.session.commit()
    except IntegrityError:
        return "Error: Grant already exists"
    
    return "Inserted"

@app.route('/grant/<grant>')
def grant(grant):
    """ Retrieves grant info for applicants to track grant progress """
    return grant.upper()