import flask
import pickle
import pandas as pd
import numpy as np
from flask import Flask, request, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy


from sklearn.preprocessing import StandardScaler

from sklearn.tree import DecisionTreeClassifier

from sklearn.ensemble import RandomForestClassifier
#load models at top of app to load into memory only one time
with open('models/loan_application_model_lr.pickle', 'rb') as f:
    clf_lr = pickle.load(f)


# with open('models/knn_regression.pkl', 'rb') as f:
#     knn = pickle.load(f)    
ss = StandardScaler()


genders_to_int = {'MALE':1,
                  'FEMALE':0}

married_to_int = {'YES':1,
                  'NO':0}

education_to_int = {'GRADUATED':1,
                  'NOT GRADUATED':0}

dependents_to_int = {'0':0,
                      '1':1,
                      '2':2,
                      '3+':3}

self_employment_to_int = {'YES':1,
                          'NO':0}                      

property_area_to_int = {'RURAL':0,
                        'SEMIRURAL':1, 
                        'URBAN':2}




app = Flask(__name__)
app.secret_key = "Secret Key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/user1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Define the path for image uploads
UPLOAD_FOLDER = 'static/Images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

# Define the User model

       

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    email = db.Column(db.String(255))
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10))

    def __init__(self, username, email, password ,role):
        self.username = username
        self.email = email
        self.password = password
        self.role = role

# Define the Admin model
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    email = db.Column(db.String(255))
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10))

    def __init__(self, username, email, password, role):
        self.username = username
        self.email = email
        self.password = password
        self.role = role

# Define the News model


# default route
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    
    # Check if username or email already exists
    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    
    if existing_user:
        return render_template('login.html', error='user_exists')
    
    new_user = User(username=username, password=password, email=email, role='user')
    db.session.add(new_user)
    db.session.commit()
    
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def login(): 
    username = request.form['username']
    password = request.form['password']
    
    # Check if the user exists in the admin table

    # Check if the user exists in the user table
    user = User.query.filter_by(username=username, password=password, role='user').first()

    if user:
        # Fetch data from the 'news' table
     
        return render_template("index.html",)  # Redirect to index.html for users
        # Fetch data from the 'news' table
     
        # Render the template 'Admin.html' and pass the news data to it
    else:
        return render_template('login.html', error='password') 





    

@app.route('/home')
def home():
    # Fetch data from the 'news' table
    return (flask.render_template("index.html") )   

@app.route('/report')
def report():
    return (flask.render_template('report.html'))

@app.route('/jointreport')
def jointreport():
    return (flask.render_template('jointreport.html'))


@app.route("/Loan_Application", methods=['GET', 'POST'])
def Loan_Application():
    
    if flask.request.method == 'GET':
        return (flask.render_template('Loan_Application.html'))
    
    if flask.request.method =='POST':
        
        #get input
        #gender as string
        genders_type = flask.request.form['genders_type']
        #marriage status as boolean YES: 1 , NO: 0
        marital_status = flask.request.form['marital_status']
        #Dependents: No. of people dependent on the applicant (0,1,2,3+)
        dependents = flask.request.form['dependents']
        
        #dependents = dependents_to_int[dependents.upper()]
        
        #education status as boolean Graduated, Not graduated.
        education_status = flask.request.form['education_status']
        #Self_Employed: If the applicant is self-employed or not (Yes, No)
        self_employment = flask.request.form['self_employment']
        #Applicant Income
        applicantIncome = float(flask.request.form['applicantIncome'])
        #Co-Applicant Income
        coapplicantIncome = float(flask.request.form['coapplicantIncome'])
        #loan amount as integer
        loan_amnt = float(flask.request.form['loan_amnt'])
        #term as integer: from 10 to 365 days...
        term_d = int(flask.request.form['term_d'])
        # credit_history
        credit_history = int(flask.request.form['credit_history'])
        # property are
        property_area = flask.request.form['property_area']
        #property_area = property_area_to_int[property_area.upper()]

        #create original output dict
        output_dict= dict()
        output_dict['Applicant Income'] = applicantIncome
        output_dict['Co-Applicant Income'] = coapplicantIncome
        output_dict['Loan Amount'] = loan_amnt
        output_dict['Loan Amount Term']=term_d
        output_dict['Credit History'] = credit_history
        output_dict['Gender'] = genders_type
        output_dict['Marital Status'] = marital_status
        output_dict['Education Level'] = education_status
        output_dict['No of Dependents'] = dependents
        output_dict['Self Employment'] = self_employment
        output_dict['Property Area'] = property_area
        


        x = np.zeros(21)
    
        x[0] = applicantIncome
        x[1] = coapplicantIncome
        x[2] = loan_amnt
        x[3] = term_d
        x[4] = credit_history

        print('------this is array data to predict-------')
        print('X = '+str(x))
        print('------------------------------------------')

        pred = clf_lr.predict([x])[0]
        
        if pred==1:
            res = '🎊🎊Congratulations! your Loan Application has been Approved!🎊🎊'
        else:
                res = '😔😔Unfortunatly your Loan Application has been Denied😔😔'
        

 
        #render form again and add prediction
        return flask.render_template('Loan_Application.html', 
                                     original_input=output_dict,
                                     result=res,)


        
        # temp = pd.DataFrame(index=[1])



        # temp['genders_type'] = genders_to_int[genders_type.upper()]
        # #marriage status as boolean YES: 1 , NO: 0
        # temp['marital_status'] = married_to_int[marital_status.upper()]
        # #Dependents: No. of people dependent on the applicant (0,1,2,3+)
        # temp['dependents'] = dependents_to_int[dependents.upper()]
        # #education status as boolean Graduated, Not graduated.
        # temp['education_status'] = education_to_int[education_status.upper()]
        # #Self_Employed: If the applicant is self-employed or not (Yes, No)
        # temp['self_employment'] = self_employment_to_int[self_employment.upper()]
        # #Applicant Income
        # temp['applicantIncome'] = applicantIncome
        # #Co-Applicant Income
        # temp['coapplicantIncome'] = coapplicantIncome
        # #loan amount as integer
        # temp['loan_amnt'] = loan_amnt
        # #term as integer: from 10 to 365 days...
        # temp['term_d'] =  term_d 
        # # credit_history
        # temp['credit_history'] = credit_history
        # # property are
        # temp['property_area'] = property_area_to_int[property_area.upper()]

        # temp['loan_amnt_log']=np.log(temp['loan_amnt'])

        # Feature Engineering :
        #temp['Total_Income']= temp['applicantIncome']+temp['coapplicantIncome']
        #temp['Total_Income_log'] = np.log(temp['Total_Income'])
        #temp['EMI']= temp['loan_amnt']/temp['term_d']
        #temp['Balance Income'] = temp['Total_Income']-(temp['EMI']*1000)

        # Columns to drop and afterward Predict up on the feature engineered columns
        #temp = temp.drop(['applicantIncome', 'coapplicantIncome', 'loan_amnt', 'term_d'], axis=1)



        # Credit_History is the most important feature followed by Balance Income, Total Income, EMI. 
        # So, feature engineering helped us in predicting our target variable.
        


        
        
            
        # #make prediction
        
        
      
if __name__ == '__main__':
    app.run(debug=True)