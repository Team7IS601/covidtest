from typing import List, Dict, Any, Tuple
import simplejson as json
from flask import Flask, request, Response, redirect
from flask import render_template
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
from flask import Flask, render_template, redirect, request,flash
from flask import Flask,render_template,flash, redirect,url_for,session,logging,request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
mysql = MySQL(cursorclass=DictCursor)
app = Flask(__name__,template_folder='templates')
app.secret_key = b'_5#y2L"F4Q8fdsfxec]/'
db = SQLAlchemy(app)

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_USER'] = 'root2'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root2'
app.config['MYSQL_DATABASE_PORT'] = 32000
app.config['MYSQL_DATABASE_DB'] = 'userData'
mysql.init_app(app)

class user(db.Model):
    username = db.Column(db.String(80), primary_key=True)
    emailaddress = db.Column(db.String(120))
    password = db.Column(db.String(80))


## --------------------- ADAM BEGIN - Register ---------------- ##
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        emailaddress = request.form['emailaddress']
        password = request.form['password']

        register = user(username = username, email = emailaddress, password = password)
        db.session.add(register)
        db.session.commit()

        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        login = user.query.filter_by(username=username, password=password).first()
        if login is not None:
            return redirect(url_for("index"))
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



if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0', debug=True)
