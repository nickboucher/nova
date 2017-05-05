# nova

*New Online-system for Vetting Applications*

Nova is an web application written in Python/Flask that will handle all grant application processing for the Harvard Undergraduate Council. From application creation to fund dispersement, nova provides online grant tracking, guided interviews, email notifications, and receipt verficiation.

## General Usage

While this application was written specifically for the Harvard Undergraduate Council, it can be easily adapted to act as a grant-application processing tool for any organization. Nova has the ability to process both *upfront* and *retroactive* grants. The typical lifecycle for each is defined as follows:

### Upfront Grants

1. Application is submitted to nova via RESTful API
2. Small grants are submitted for review by a staff member, while larger grants are invited in for an interview
3. Grant recommendations are up for review by the Financial Committee
4. Grant recommendatiosn are up for review by the General Council
5. Funds are dispensed
6. Receipts are submitted via RESTful API
7. Receipts are reviewed by treasurer and grant is finalized


### Retroactive Grants

1. Application is submitted to nova via RESTful API
2. Small grants are submitted for review by a staff member, while larger grants are invited in for an interview
3. Grant recommendations are up for review by the Financial Committee
4. Grant recommendatiosn are up for review by the General Council
5. Receipts are submitted via RESTful API
6. Receipts are reviewed by treasurer
7. Funds are dispensed


## Installation

nova is implemented in Python3 using the Flask microframework. Installation is performed via the following steps:

1. Clone all repository files onto server
2. Configure a Flask deployment setup as defined [here](http://flask.pocoo.org/docs/latest/deploying/)
3. Run *installation.py* to configure local setup
4. Optionally, run *dummy_data.py* to test the installation with fake grant applications
