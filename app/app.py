from typing import List, Dict, Any, Tuple
import simplejson as json
from flask import Flask, request, Response, redirect
from flask import render_template
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor

app = Flask(__name__)
mysql = MySQL(cursorclass=DictCursor)
app = Flask(__name__,template_folder='templates')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/",methods=['POST'])
def other1():
    symptoms = request.form.getlist('checkbox')
    if len(symptoms) > 8:
        flash('You do not meet the criteria for testing, have a nice day! Stay Healthy!')
        return redirect("/")
    else:
        return redirect('/schedule')



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
