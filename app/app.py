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

app = Flask(__name__)
mysql = MySQL(cursorclass=DictCursor)
app = Flask(__name__,
            template_folder='templates',
            static_url_path='',
            static_folder='static',)
app.secret_key = b'_5#y2L"F4Q8fdsfxec]/'
db = SQLAlchemy(app)
socketio = SocketIO(app)

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_PORT'] = 32000
app.config['MYSQL_DATABASE_DB'] = 'userData'
mysql.init_app(app)

class user(db.Model):
    username = db.Column(db.String(80), primary_key=True)
    emailaddress = db.Column(db.String(120))
    password = db.Column(db.String(80))


########## RYAN BEGIN ----- CALENDAR --------------- #########

@app.route('/Calendar')
def index():
    if 'credentials' not in flask.session:
      return flask.redirect(flask.url_for('oauth2callback'))
    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    if credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))
    return flask.render_template('calendar.html')



## --------------------- ADAM BEGIN - Register ---------------- ##
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        emailaddress = request.form['emailaddress']
        password = request.form['password']

        register = user(username = username, emailaddress = emailaddress, password = password)
        db.session.add(register)
        db.session.commit()

        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        cursor = mysql.get_db().cursor()
        inputData = (request.form.get('username'), request.form.get('emailaddress'), request.form.get('password'))
        sql_insert_query = """INSERT INTO tbluserDataImport (username,emailaddress,password) VALUES (%s,%s,%s) """
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
