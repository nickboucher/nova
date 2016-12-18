from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
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
    return request.args.get('grant_id')

@app.route('/grant/<grant>')
def grant(grant):
    """ Example of how to have each grant use its own URL """
    return grant