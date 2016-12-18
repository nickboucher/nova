from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from datetime import datetime
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

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/new_grant')
def new_grant():
    """ Example of how to pass info to web app via Query Strings """
    
    grant = Grant("35S-1-3")
    
    if request.args.get('amount_requested'): grant.amount_requested = float(request.args.get('amount_requested'))
    if request.args.get('is_collaboration'): grant.is_collaboration = (True if request.args.get('is_collaboration') == "Yes" else False)
    if request.args.get('collaborators'): grant.collaborators = request.args.get('collaborators')
    if request.args.get('collaboration_explanation'): grant.collaboration_explanation = request.args.get('collaboration_explanation')
    if request.args.get('contact_first_name'): grant.contact_first_name = request.args.get('contact_first_name')
    if request.args.get('contact_last_name'): grant.contact_last_name = request.args.get('contact_last_name')
    if request.args.get('contact_email'): grant.contact_email = request.args.get('contact_email')
    if request.args.get('contact_phone'): grant.contact_phone = request.args.get('contact_phone')
    if request.args.get('contact_role'): grant.contact_role = request.args.get('contact_role')
    if request.args.get('is_upfront'): grant.is_upfront = (True if request.args.get('is_upfront') == "1" else False)
    if request.args.get('organization'): grant.organization = request.args.get('organization')
    if request.args.get('tax_id'): grant.tax_id = request.args.get('tax_id')
    if request.args.get('project'): grant.project = request.args.get('project')
    if request.args.get('project_description'): grant.project_description = request.args.get('project_description')
    if request.args.get('is_event'): grant.is_event = (True if request.args.get('is_event') == "Event" else False)
    if request.args.get('project_location'): grant.project_location = request.args.get('project_location')
    if request.args.get('project_start'): grant.project_start = datetime.strptime(request.args.get('project_start'), '%m/%d/%Y')
    if request.args.get('project_end'): grant.project_end = datetime.strptime(request.args.get('project_end'), '%m/%d/%Y')
    if request.args.get('college_attendees'): grant.college_attendees = int(request.args.get('college_attendees'))
    if request.args.get('facebook_link'): grant.facebook_link = request.args.get('facebook_link')
    if request.args.get('revenue1_type'): grant.revenue1_type = request.args.get('revenue1_type')
    if request.args.get('revenue1_description'): grant.revenue1_description = request.args.get('revenue1_description')
    if request.args.get('revenue1_amount'): grant.revenue1_amount = float(request.args.get('revenue1_amount'))
    if request.args.get('revenue2_type'): grant.revenue2_type = request.args.get('revenue2_type')
    if request.args.get('revenue2_description'): grant.revenue2_description = request.args.get('revenue2_description')
    if request.args.get('revenue2_amount'): grant.revenue2_amount = float(request.args.get('revenue2_amount'))
    if request.args.get('revenue3_type'): grant.revenue3_type = request.args.get('revenue3_type')
    if request.args.get('revenue3_description'): grant.revenue3_description = request.args.get('revenue3_description')
    if request.args.get('revenue3_amount'): grant.revenue3_amount = float(request.args.get('revenue3_amount'))
    if request.args.get('revenue4_type'): grant.revenue4_type = request.args.get('revenue4_type')
    if request.args.get('revenue4_description'): grant.revenue4_description = request.args.get('revenue4_description')
    if request.args.get('revenue4_amount'): grant.revenue4_amount = float(request.args.get('revenue4_amount'))
    if request.args.get('revenue5_type'): grant.revenue5_type = request.args.get('revenue5_type')
    if request.args.get('revenue5_description'): grant.revenue5_description = request.args.get('revenue5_description')
    if request.args.get('revenue5_amount'): grant.revenue5_amount = float(request.args.get('revenue5_amount'))
    if request.args.get('revenue6_type'): grant.revenue6_type = request.args.get('revenue6_type')
    if request.args.get('revenue6_description'): grant.revenue6_description = request.args.get('revenue6_description')
    if request.args.get('revenue6_amount'): grant.revenue6_amount = float(request.args.get('revenue6_amount'))
    if request.args.get('revenue7_type'): grant.revenue7_type = request.args.get('revenue7_type')
    if request.args.get('revenue7_description'): grant.revenue7_description = request.args.get('revenue7_description')
    if request.args.get('revenue7_amount'): grant.revenue7_amount = float(request.args.get('revenue7_amount'))
    if request.args.get('revenue8_type'): grant.revenue8_type = request.args.get('revenue8_type')
    if request.args.get('revenue8_description'): grant.revenue8_description = request.args.get('revenue8_description')
    if request.args.get('revenue8_amount'): grant.revenue8_amount = float(request.args.get('revenue8_amount'))
    if request.args.get('revenue9_type'): grant.revenue9_type = request.args.get('revenue9_type')
    if request.args.get('revenue9_amount'): grant.revenue9_amount = float(request.args.get('revenue9_amount'))
    if request.args.get('revenue10_type'): grant.revenue10_type = request.args.get('revenue10_type')
    if request.args.get('revenue10_description'): grant.revenue10_description = request.args.get('revenue10_description')
    if request.args.get('revenue10_amount'): grant.revenue10_amount = float(request.args.get('revenue10_amount'))
    if request.args.get('app_expense1_type'): grant.app_expense1_type = request.args.get('app_expense1_type')
    if request.args.get('app_expense1_description'): grant.app_expense1_description = request.args.get('app_expense1_description')
    if request.args.get('app_expense1_amount'): grant.app_expense1_amount = float(request.args.get('app_expense1_amount'))
    if request.args.get('app_expense2_type'): grant.app_expense2_type = request.args.get('app_expense2_type')
    if request.args.get('app_expense2_description'): grant.app_expense2_description = request.args.get('app_expense2_description')
    if request.args.get('app_expense2_amount'): grant.app_expense2_amount = float(request.args.get('app_expense2_amount'))
    if request.args.get('app_expense3_type'): grant.app_expense3_type = request.args.get('app_expense3_type')
    if request.args.get('app_expense3_description'): grant.app_expense3_description = request.args.get('app_expense3_description')
    if request.args.get('app_expense3_amount'): grant.app_expense3_amount = float(request.args.get('app_expense3_amount'))
    if request.args.get('app_expense4_type'): grant.app_expense4_type = request.args.get('app_expense4_type')
    if request.args.get('app_expense4_description'): grant.app_expense4_description = request.args.get('app_expense4_description')
    if request.args.get('app_expense4_amount'): grant.app_expense4_amount = float(request.args.get('app_expense4_amount'))
    if request.args.get('app_expense5_type'): grant.app_expense5_type = request.args.get('app_expense5_type')
    if request.args.get('app_expense5_description'): grant.app_expense5_description = request.args.get('app_expense5_description')
    if request.args.get('app_expense5_amount'): grant.app_expense5_amount = float(request.args.get('app_expense5_amount'))
    if request.args.get('app_expense6_type'): grant.app_expense6_type = request.args.get('app_expense6_type')
    if request.args.get('app_expense6_description'): grant.app_expense6_description = request.args.get('app_expense6_description')
    if request.args.get('app_expense6_amount'): grant.app_expense6_amount = float(request.args.get('app_expense6_amount'))
    if request.args.get('app_expense7_type'): grant.app_expense7_type = request.args.get('app_expense7_type')
    if request.args.get('app_expense7_description'): grant.app_expense7_description = request.args.get('app_expense7_description')
    if request.args.get('app_expense7_amount'): grant.app_expense7_amount = float(request.args.get('app_expense7_amount'))
    if request.args.get('app_expense8_type'): grant.app_expense8_type = request.args.get('app_expense8_type')
    if request.args.get('app_expense8_description'): grant.app_expense8_description = request.args.get('app_expense8_description')
    if request.args.get('app_expense8_amount'): grant.app_expense8_amount = float(request.args.get('app_expense8_amount'))
    if request.args.get('app_expense9_type'): grant.app_expense9_type = request.args.get('app_expense9_type')
    if request.args.get('app_expense9_description'): grant.app_expense9_description = request.args.get('app_expense9_description')
    if request.args.get('app_expense9_amount'): grant.app_expense9_amount = float(request.args.get('app_expense9_amount'))
    if request.args.get('app_expense10_type'): grant.app_expense10_type = request.args.get('app_expense10_type')
    if request.args.get('app_expense10_description'): grant.app_expense10_description = request.args.get('app_expense10_description')
    if request.args.get('app_expense10_amount'): grant.app_expense10_amount = float(request.args.get('app_expense10_amount'))
    if request.args.get('app_expense11_type'): grant.app_expense11_type = request.args.get('app_expense11_type')
    if request.args.get('app_expense11_description'): grant.app_expense11_description = request.args.get('app_expense11_description')
    if request.args.get('app_expense11_amount'): grant.app_expense11_amount = float(request.args.get('app_expense11_amount'))
    if request.args.get('app_expense12_type'): grant.app_expense12_type = request.args.get('app_expense12_type')
    if request.args.get('app_expense12_description'): grant.app_expense12_description = request.args.get('app_expense12_description')
    if request.args.get('app_expense12_amount'): grant.app_expense12_amount = float(request.args.get('app_expense12_amount'))
    if request.args.get('application_comments'): grant.application_comments = request.args.get('application_comments')
    
    try:
        db.session.add(grant)
        db.session.commit()
    except IntegrityError:
        return "Error: Grant already exists"
    
    return "Inserted"

@app.route('/grant/<grant>')
def grant(grant):
    """ Example of how to have each grant use its own URL """
    return grant