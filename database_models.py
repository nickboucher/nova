#
# database_models.py
# Nicholas Boucher 2017
#
# Contains the Python Class models used to map the SQLlite database to
# the application via SQLAlchemy
#

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin as FlaskLoginUser
from datetime import datetime

# Initialize db variable to avoid namespace errors
# ('db' must be imported by application later)
db = SQLAlchemy()

# Set the small grant dollar amount cap
small_grant_cap = 200.00
# Set small grant elligible funding categories
small_grant_expense_types = ['Food', 'Publicity']

#
# --------- Database Models -----------
#

class Grant(db.Model):
    """ Contains all information about any grant application (and its current progress) """
    # General Grant Info
    id = db.Column(db.Integer, primary_key=True)
    grant_id = db.Column(db.Text, unique=True)
    # Application Info
    application_submit_time = db.Column(db.DateTime, default=datetime.utcnow)
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
    # Small Grant Info
    is_small_grant = db.Column(db.Boolean, default=False)
    small_grant_is_reviewed = db.Column(db.Boolean, default=False) # (non-small grants don't use this)
    small_grant_reviewer = db.Column(db.Text) # (non-small grants don't use this)
    small_grant_review_date = db.Column(db.DateTime) # (non-small grants don't use this)
    # Interview Info
    interviewer = db.Column(db.Text) # (small grants don't use this)
    interview_occurred = db.Column(db.Boolean, default=False) # (small grants don't use this)
    interview_date = db.Column(db.DateTime) # date interview actually ocurred (small grants don't use this)
    interview_schedule_date = db.Column(db.DateTime) # Next scheduled interview
    interview_schedule_history = db.Column(db.Text) # comma-separated interview scheduled times
    interviewer_notes = db.Column(db.Text)
    food_allocated = db.Column(db.Float) # Does not include cuts
    food_allocated_notes = db.Column(db.Text)
    travel_allocated = db.Column(db.Float) # Does not include cuts
    travel_allocated_notes = db.Column(db.Text)
    publicity_allocated = db.Column(db.Float) # Does not include cuts
    publicity_allocated_notes = db.Column(db.Text)
    materials_allocated = db.Column(db.Float) # Does not include cuts
    materials_allocated_notes = db.Column(db.Text)
    venue_allocated = db.Column(db.Float) # Does not include cuts
    venue_allocated_notes = db.Column(db.Text)
    decorations_allocated = db.Column(db.Float) # Does not include cuts
    decorations_allocated_notes = db.Column(db.Text)
    media_allocated = db.Column(db.Float) # Does not include cuts
    media_allocated_notes = db.Column(db.Text)
    admissions_allocated = db.Column(db.Float) # Does not include cuts
    admissions_allocated_notes = db.Column(db.Text)
    hupd_allocated = db.Column(db.Float) # Does not include cuts
    hupd_allocated_notes = db.Column(db.Text)
    personnel_allocated = db.Column(db.Float) # Does not include cuts
    personnel_allocated_notes = db.Column(db.Text)
    other_allocated = db.Column(db.Float) # Does not include cuts
    other_allocated_notes = db.Column(db.Text)
    percentage_cut = db.Column(db.Float) # Decimal Number in [0,100] representing percentage deducted due to cuts
    amount_allocated = db.Column(db.Float) # Total Amount allocated with all cuts factored in
    is_collaboration_confirmed = db.Column(db.Boolean)
    receipts_due_date = db.Column(db.Boolean)
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
    receipts_submit_date = db.Column(db.DateTime)
    receipts_submitted = db.Column(db.Boolean, default=False)
    receipts_resubmit_history = db.Column(db.Text) # comma-separated list of resubmission dates
    # Grants Pack Info
    grants_pack = db.Column(db.Text)
    council_approved = db.Column(db.Boolean, default=False)
    # Treasurer Info
    is_paid = db.Column(db.Boolean, default=False)
    receipts_reviewed = db.Column(db.Boolean, default=False)
    pay_date = db.Column(db.DateTime)
    receipts_reviewer = db.Column(db.Text)
    is_direct_deposit = db.Column(db.Boolean)
    check_number = db.Column(db.Text)
    amount_dispensed = db.Column(db.Float)
    treasurer_notes = db.Column(db.Text)
    amount_spent = db.Column(db.Float)
    must_reimburse_uc = db.Column(db.Boolean, default=False) # If club didn't spend as much as upfront grant gave
    reimburse_uc_amount = db.Column(db.Float) # Amount club owes/owed UC
    reimbursed_uc = db.Column(db.Boolean, default=False) # If club paid us back
    


    def __init__(self, grant_id):
        self.grant_id = grant_id

    def __repr__(self):
        return '<Grant %r>' % self.grant_id

class Organization(db.Model):
    """ Contains information about student organizations on campus """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, unique=True)
    bank_name = db.Column(db.Text)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Organization %r>' % self.name
        
class Config(db.Model):
    """ Contains configuration <key,value> pairs used for general application setup """
    key = db.Column(db.Text, primary_key=True)
    value = db.Column(db.Text)

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __repr__(self):
        return '<Config %r>' % self.key
        
class Grants_Week(db.Model):
    """ Contains the number of grants submitted in each grant week, used to generate new Grant IDs,
        as well as information about the status of the associated grants pack """
    grant_week = db.Column(db.String(64), primary_key=True)
    num_grants = db.Column(db.Integer) # Note: Not all of these will necessarily be in this week's grants pack
    grants_pack_finalized = db.Column(db.Boolean, default=False) # Finalized once approved by council, which locks it for editing
    budget = db.Column(db.Float, default=10000) # Weekly budget
    requested = db.Column(db.Float) # Dollar amount requested by all grants in this grants pack
    allocated = db.Column(db.Float) # Dollar amount allocated in this grants_pack when finalized

    def __init__(self, grant_week):
        self.grant_week = grant_week
        self.num_grants = 0

    def __repr__(self):
        return '<Grants_Week %r>' % self.grant_week
        
class User(db.Model, FlaskLoginUser):
    """ Implements a User class that can be accessed by flask-login and handled by flask-sqlalchemy """
    
    email = db.Column(db.Text, primary_key=True)
    first_name = db.Column(db.Text)
    last_name = db.Column(db.Text)
    admin = db.Column(db.Boolean, default=False)
    pw_hash = db.Column(db.Text)
    salt = db.Column(db.Text)
    
    def __init__(self, email, first_name, last_name, admin, pw_hash, salt):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.admin = admin
        self.pw_hash = pw_hash
        self.salt = salt
        
    def get_id(self):
        return self.email
        
    def __repr__(self):
        return '<User %r>' % self.email