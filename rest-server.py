#!flask/bin/python
from __future__ import print_function
from flask import Flask, jsonify, abort, request, make_response, url_for
from flask import render_template, redirect


import sqlite3
import MySQLdb

import sys

HOST = "159.203.125.202"
USER = "remote"
PASS = "login"
DB = "test" 
PORT = 3306

    
app = Flask(__name__, static_url_path="")

@app.route('/', methods=['GET'])
def home_page():
    conn = MySQLdb.connect (host = HOST,
                            user = USER,
                            passwd = PASS,
                            db = DB, 
                            port = 3306)
    if conn:
        print("Connection successful")
    else:
    	print("Connection unsuccessful")

    return render_template('index.html')


@app.route('/pickupTimes', methods=['GET'])
def view_times():
    return render_template('pickUpTimes.html')


@app.route('/historicalData', methods=['GET'])
def view_history():       
    return render_template('historicalData.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
    
