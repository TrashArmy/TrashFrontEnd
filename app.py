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


@app.route('/', methods=['GET'])
def home_page():
    global dbcount, flag
    conn = MySQLdb.connect (host = HOST,
                            user = USER,
                            passwd = PASS,
                            db = DB, 
                            port = 3306)
    cursor = conn.cursor();

    fillLevel = [0,0,0,0]
    timeStamp = [datetime(2000, 3, 9, 9, 11, 12),datetime(2000, 3, 9, 9, 11, 12),datetime(2000, 3, 9, 9, 11, 12),datetime(2000, 3, 9, 9, 11, 12)]
    
    #Bin 0 Fill Level
    cursor.execute("SELECT * FROM TrashData WHERE trashCanId=0 AND binId=0;");
    results = cursor.fetchall();
    for item in results:
    	if item[2] > timeStamp[0]:
    		timeStamp[0] = item[2]
    		fillLevel[0] = item[3]

    #Bin 1 Fill Level
    cursor.execute("SELECT * FROM TrashData WHERE trashCanId=0 AND binId=1;");
    results = cursor.fetchall();
    for item in results:
    	if item[2] > timeStamp[1]:
    		timeStamp[1] = item[2]
    		fillLevel[1] = item[3]

    #Bin 2 Fill Level
    cursor.execute("SELECT * FROM TrashData WHERE trashCanId=0 AND binId=2;");
    results = cursor.fetchall();
    for item in results:
    	if item[2] > timeStamp[2]:
    		timeStamp[2] = item[2]
    		fillLevel[2] = item[3]

    #Bin 3 Fill Level
    cursor.execute("SELECT * FROM TrashData WHERE trashCanId=0 AND binId=3;");
    results = cursor.fetchall();
    for item in results:
    	if item[2] > timeStamp[3]:
    		timeStamp[3] = item[2]
    		fillLevel[3] = item[3]
    print("Initial fill level of landfil " + str(fillLevel[3]))
    cursor.close()
    conn.close
    return render_template('index.html', bin0 = fillLevel[0], bin1 = fillLevel[1], bin2 = fillLevel[2], bin3 = fillLevel[3], hello = "string")


@app.route('/pickupTimes', methods=['GET'])
def view_times():
    paperTime = calcPickUpTime(0)
    alumTime = calcPickUpTime(1)
    plasticTime = calcPickUpTime(2)
    landfillTime = calcPickUpTime(3)
    return render_template('pickUpTimes.html', paperTime = paperTime, alumTime = alumTime, 
        plasticTime= plasticTime, landfillTime = landfillTime )

def calcPickUpTime(binId):
    paperTime = ""
    paperFillRate = calcAvgFillRate(binId)
    paperData = getFillData(binId)
    if paperFillRate is None:
        paperTime = "Not enough data!"
    else:
        if len(paperData) == 0:
            now = datetime.datetime.now()
            paperTime = now + paperFillRate
        else:
            currFill = paperData[len(paperData) - 1]['fill'] 
            percent = (100 - int(currFill)/100)
            dateobj = datetime.strptime(paperData[len(paperData) - 1]['date'], '%Y-%m-%d %H:%M:%S')
            paperTime =  dateobj + paperFillRate*percent   
            paperTime = paperTime.strftime('%b %d %H:%M') 
    return paperTime;


@app.route('/historicalData', methods=['GET'])
def view_history():
    paperData = getFillData(0)
    alumData = getFillData(1)
    plasticData = getFillData(2)
    landfillData = getFillData(3)
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
    # # Take note of number of entries in db
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



