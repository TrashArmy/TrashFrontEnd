#!flask/bin/python
from __future__ import print_function
from flask import Flask, jsonify, abort, request, make_response, url_for, render_template, session
from flask import render_template, redirect
from datetime import datetime
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
import time
import MySQLdb
import sys
import json

HOST = "159.203.125.202"
USER = "remote"
PASS = "login"
DB = "SeniorDesign" 
PORT = 3306

app = Flask(__name__, static_url_path="")

#! Socket Shtuff
async_mode = None
socketio = SocketIO(app, async_mode= async_mode)
#!

dbcount = 100000000000000
PAPER = 0
LANDFILL = 1
PLASTIC = 2
ALUMINUM = 3
fillLevel = [0,0,0,0]
timeStamp = [datetime(2000, 3, 9, 9, 11, 12),datetime(2000, 3, 9, 9, 11, 12),datetime(2000, 3, 9, 9, 11, 12),datetime(2000, 3, 9, 9, 11, 12)]


@app.route('/', methods=['GET'])
def home_page():
    global dbcount, PAPER, LANDFILL, PLASTIC, ALUMINUM, fillLevel, timeStamp
    conn = MySQLdb.connect (host = HOST,
                            user = USER,
                            passwd = PASS,
                            db = DB, 
                            port = 3306)
    cursor = conn.cursor();
    getFillLevel(PAPER, cursor)
    getFillLevel(LANDFILL, cursor)
    getFillLevel(PLASTIC, cursor)
    getFillLevel(ALUMINUM, cursor)
    cursor.close()
    conn.close
    return render_template('index.html', paper = fillLevel[PAPER], landfill = fillLevel[LANDFILL], plastic = fillLevel[PLASTIC], aluminum = fillLevel[ALUMINUM])

def getFillLevel(binNum, cursor):
    global fillLevel, timeStamp
    cursor.execute("SELECT * FROM TrashData WHERE trashCanId=0 AND binId=" + str(binNum) + " ;");
    results = cursor.fetchall();
    one = {}
    for item in results:
        if item[2] > timeStamp[binNum]:
            timeStamp[binNum] = item[2]
            fillLevel[binNum] = item[3]     

@app.route('/pickupTimes', methods=['GET'])
def view_times():
    paperTime = calcPickUpTime(PAPER)
    alumTime = calcPickUpTime(ALUMINUM)
    plasticTime = calcPickUpTime(PLASTIC)
    landfillTime = calcPickUpTime(LANDFILL)
    return render_template('pickUpTimes.html', paperTime = paperTime, alumTime = alumTime, 
        plasticTime= plasticTime, landfillTime = landfillTime )

def calcPickUpTime(binId):
    time = ""
    fillRate = calcAvgFillRate(binId)
    data = getFillData(binId)
    if fillRate is None:
        time = "Not enough data!"
    else:
        if len(data) == 0:
            now = datetime.datetime.now()
            time = now + fillRate
        else:
            currFill = data[len(data) - 1]['fill'] 
            percent = (100 - int(currFill)/100)
            dateobj = datetime.strptime(data[len(data) - 1]['date'], '%Y-%m-%d %H:%M:%S')
            time =  dateobj + fillRate*percent   
            time = time.strftime('%b %d %H:%M') 
    return time;


@app.route('/historicalData', methods=['GET'])
def view_history():
    paperData = getFillData(PAPER)
    alumData = getFillData(ALUMINUM)
    plasticData = getFillData(PLASTIC)
    landfillData = getFillData(LANDFILL)
    return render_template('historicalData.html', paperData = json.dumps(paperData), 
        alumData =json.dumps(alumData), plasticData =json.dumps(plasticData), landfillData = json.dumps(landfillData) )

def calcAvgFillRate(binNum):
    conn = MySQLdb.connect (host = HOST,
                            user = USER,
                            passwd = PASS,
                            db = DB, 
                            port = 3306)
    cursor = conn.cursor();
    cmd = "SELECT * FROM TrashData WHERE trashCanId=0 AND binId=" + str(binNum) + " AND emptied=1;"
    cursor.execute(cmd);
    results = cursor.fetchall();
    length = len(results)
    lastDate = None
    count = 0
    avgEmptyRate = None
    if length >= 2:
        for result in results:
            if lastDate is None:
                lastDate = result[2];
            else:
                currDate = result[2]
                diff = currDate - lastDate
                lastDate = result[2]
                if avgEmptyRate is None:
                    avgEmptyRate = diff;
                else:
                    avgEmptyRate = (avgEmptyRate*count + diff)/(count + 1)
            count = count + 1;
    return avgEmptyRate;

def getFillData(binId):
    conn = MySQLdb.connect (host = HOST,
                            user = USER,
                            passwd = PASS,
                            db = DB, 
                            port = 3306)
    cursor = conn.cursor();
    cmd = "SELECT * FROM TrashData WHERE trashCanId=0 AND binId=" + str(binId) + " AND emptied=1;"
    cursor.execute(cmd);
    results = cursor.fetchall();
    dateLastEmptied = results[-1][2]
    cmd = "SELECT * FROM TrashData WHERE trashCanId=0 AND binId=" + str(binId) + " AND timestamp > '" + str(dateLastEmptied) + "'"
    cursor.execute(cmd)
    results = cursor.fetchall()
    data = []
    for item in results:
        one = {}
        one['date'] = str(item[2]);
        one['fill'] = str(item[3]);
        data.append(one);
    return data

@socketio.on('connect', namespace='/test')
def test_connect():
    print("Connected on server side!")
    global thread, socketio


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)


@socketio.on('check_db', namespace='/test')
def check_db():
    global dbcount, socketio
    conn = MySQLdb.connect (host = HOST,
                            user = USER,
                            passwd = PASS,
                            db = DB, 
                            port = 3306)
    cursor = conn.cursor();
    # Take note of number of entries in db
    cursor.execute(" SELECT COUNT(*) FROM TrashData");
    results = cursor.fetchall();
    currentCount = int(results[0][0])
    oldCount = dbcount
    dbcount = currentCount
    if(currentCount > oldCount):
        print("Diff detected")
        diff = currentCount - oldCount
        dbcount = currentCount
        print("Current diff " + str(diff))
        cmd = "SELECT * FROM TrashData ORDER BY timestamp DESC LIMIT " + str(diff)
        cursor.execute(cmd)
        new_entries = cursor.fetchall();
        for item in new_entries:
            print("Update deets: bin" + str(item[1]) + "fillLevel " + str(item[3]))
            socketio.emit('update_gauges',
                  {'bin': str(item[1]), 'fillLevel': str(item[3])},
                  namespace='/test')
            socketio.sleep(10)
    cursor.close();


if __name__ == '__main__':
    #!app.run(debug=True, port=5000)
    socketio.run(app, debug=True)



