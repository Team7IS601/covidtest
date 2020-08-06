#!/usr/local/bin/python
from typing import List, Dict, Any, Tuple
import simplejson as json
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
from flask import Flask,render_template,flash, redirect,url_for,session,logging,request
from flask_sqlalchemy import SQLAlchemy
import sys, json, flask, flask_socketio, httplib2, uuid
from flask import Response, request
from flask_socketio import SocketIO
from apiclient import discovery
from oauth2client import client
from googleapiclient import sample_tools
from rfc3339 import rfc3339
from dateutil import parser

mysql = MySQL(cursorclass=DictCursor)
app = Flask(__name__,
            template_folder='templates',
            static_url_path='',
            static_folder='static',)
app.secret_key = b'_5#y2L"F4Q8fdsfxec]/'
db = SQLAlchemy(app)
socketio = SocketIO(app)

app.config['MYSQL_DATABASE_HOST'] = 'db'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'fidelio'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_DB'] = 'userData'
mysql.init_app(app)

class user(db.Model):
    username = db.Column(db.String(80), primary_key=True)
    emailaddress = db.Column(db.String(120))
    password = db.Column(db.String(80))


########## RYAN BEGIN ----- CALENDAR --------------- #########

@app.route('/Calendar')
def calendar():
    if 'credentials' not in flask.session:
      return flask.redirect(flask.url_for('oauth2callback'))
    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    if credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))
    return flask.render_template('calendar.html')

#Begin oauth callback route
@app.route('/oauth2callback')
def oauth2callback():
  flow = client.flow_from_clientsecrets(
      'client_secrets.json',
      scope='https://www.googleapis.com/auth/calendar',
      redirect_uri=flask.url_for('oauth2callback', _external=True))
  if 'code' not in flask.request.args:
    auth_uri = flow.step1_get_authorize_url()
    return flask.redirect(auth_uri)
  else:
    auth_code = flask.request.args.get('code')
    credentials = flow.step2_exchange(auth_code)
    flask.session['credentials'] = credentials.to_json()
    return flask.redirect(flask.url_for('index'))

#On event submission from client
@socketio.on('eventDesc')
def eventDesc(data):
    print("INSIDE eventDesc!!!")
    name = data['name']
    sTime =  parser.parse(data['sTime'])
    eTime =  parser.parse(data['eTime'])
    cid = data['cid']
    sConverted = rfc3339(sTime)
    eConverted = rfc3339(eTime)
    oauth(name, cid, sConverted, eConverted)

#On getCalendars event from client. Gets the calendar names and their corresponding ID's
@socketio.on("getCalendars")
def getCalendars():
    calendars = []
    try:
        credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    except credError:
        print("did not assign credentials")
    http_auth = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http_auth)
    page_token = None
    while True:
      calendar_list = service.calendarList().list(pageToken=page_token).execute()
      for calendar_list_entry in calendar_list['items']:
        calendars.append({"name": calendar_list_entry['summary'], "id": calendar_list_entry['id']})
      page_token = calendar_list.get('nextPageToken')
      if not page_token:
        break
    flask_socketio.emit("calendarReturn", {"data": calendars})

#Function to add event into calendar selected
def oauth(name, cid, sTime, eTime):
    print(sTime)
    print(eTime)
    print(name)
    print(cid)
    try:
        credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    except credError:
        print("did not assign credentials")
    http_auth = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http_auth)
    eventName = ""
    event = {
        'summary': name,
        'start': {
        'dateTime': sTime
        },
        'end': {
        'dateTime': eTime
        },
        'iCalUID': 'originalUID'
    }
    imported_event = service.events().import_(calendarId=cid, body=event).execute()
    print("Succesfully Imported Event")




## --------------------- ADAM BEGIN - Register ---------------- ##
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        emailaddress = request.form['emailaddress']
        password = request.form['password']
        inputData = (username, emailaddress, password)
        sql_insert_query = """INSERT INTO tbluserDataImport (username,emailaddress,password) VALUES (%s,%s,%s)"""
        cursor = mysql.get_db().cursor()
        cursor.execute(sql_insert_query, inputData)
        mysql.get_db().commit()
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        inputData = (request.form.get('username'), request.form.get('emailaddress'), request.form.get('password'))
        sql_insert_query = """INSERT INTO tbluserDataImport (username,emailaddress,password) VALUES (%s,%s,%s) """

        cursor = mysql.get_db().cursor()
        cursor.execute(sql_insert_query, inputData)
        login = user.query.filter_by(username=username, password=password).first()
        if login is not None:
            flash('Wrong Password, Try Again')
            return redirect("/")
    return render_template("login.html")


## --------------------- ADAM END - Register ---------------- ##

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/",methods=['POST'])
def other1():
    symptoms = request.form.getlist('checkbox')
    if len(symptoms) < 8:
        flash('You do not meet the criteria for testing, have a nice day! Stay Healthy!')
        return redirect("/")
    else:
        return redirect('/register')




@app.route("/logout")
def logout():
	"""Logout Form"""
	session['logged_in'] = False
	return redirect(url_for('/'))

if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0', debug=True)
    app.secret_key = str(uuid.uuid4())
