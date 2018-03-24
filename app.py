#!flask/bin/python
from __future__ import print_function
from flask import Flask, jsonify, abort, request, make_response, url_for, render_template, session
from flask import render_template, redirect
from datetime import datetime
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
from threading import Lock
import time

import sqlite3
import MySQLdb

import sys

HOST = "159.203.125.202"
USER = "remote"
PASS = "login"
DB = "SeniorDesign" 
PORT = 3306

 

app = Flask(__name__, static_url_path="")

#! Socket Shtuff
async_mode = None
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()
#!

#! Socket Shtuff
def background_thread():
    # Connect to MySql db
    print("Entering thread")
    conn = MySQLdb.connect (host = HOST,
                            user = USER,
                            passwd = PASS,
                            db = DB, 
                            port = 3306)
    cursor = conn.cursor();

    # Take note of number of entries in db
    cursor.execute(" SELECT COUNT(*) FROM TrashData");
    results = cursor.fetchall();
    count = int(results[0][0])
    diff = 0
    print("Current count " + str(count))

    # Continually check for change in number of db elements
    while True:
        cursor = conn.cursor();
        conn.begin();
        cursor.execute(" SELECT COUNT(*) FROM TrashData");
        currentCount = cursor.fetchall();
        if(int(currentCount[0][0]) > count):
            print("Diff detected")
            diff = int(currentCount[0][0]) - count
            count = int(currentCount[0][0])
            print("Current count " + str(count))
            cmd = "SELECT * FROM TrashData ORDER BY timestamp DESC LIMIT " + str(diff)
            cursor.execute(cmd)
            new_entries = cursor.fetchall();
            for item in new_entries:
                print("Update deets: bin" + str(item[1]) + "fillLevel " + str(item[3]))
                socketio.emit('my_response',
                      {'bin': str(item[1]), 'fillLevel': str(item[3])},
                      namespace='/test')
                socketio.sleep(10)
        cursor.close();

#!

@app.route('/', methods=['GET'])
def home_page():
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

    return render_template('index.html', bin0 = fillLevel[0], bin1 = fillLevel[1], bin2 = fillLevel[2], bin3 = fillLevel[3])


@app.route('/pickupTimes', methods=['GET'])
def view_times():
    return render_template('pickUpTimes.html')


@app.route('/historicalData', methods=['GET'])
def view_history():       
    return render_template('historicalData.html')

#! Socketsss
@socketio.on('my_event', namespace='/test')
def test_message(message):
    print("Got my event, next should go to my response")
    # session['receive_count'] = session.get('receive_count', 0) + 1
    # emit('my_response',
    #      {'data': message['data'], 'count': session['receive_count']})


# @socketio.on('my_broadcast_event', namespace='/test')
# def test_broadcast_message(message):
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     emit('my_response',
#          {'data': message['data'], 'count': session['receive_count']},
#          broadcast=True)


# @socketio.on('join', namespace='/test')
# def join(message):
#     join_room(message['room'])
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     emit('my_response',
#          {'data': 'In rooms: ' + ', '.join(rooms()),
#           'count': session['receive_count']})


# @socketio.on('leave', namespace='/test')
# def leave(message):
#     leave_room(message['room'])
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     emit('my_response',
#          {'data': 'In rooms: ' + ', '.join(rooms()),
#           'count': session['receive_count']})


# @socketio.on('close_room', namespace='/test')
# def close(message):
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
#                          'count': session['receive_count']},
#          room=message['room'])
#     close_room(message['room'])


# @socketio.on('my_room_event', namespace='/test')
# def send_room_message(message):
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     emit('my_response',
#          {'data': message['data'], 'count': session['receive_count']},
#          room=message['room'])


@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()


# @socketio.on('my_ping', namespace='/test')
# def ping_pong():
#     emit('my_pong')


@socketio.on('connect', namespace='/test')
def test_connect():
    print("Connected in app.py")
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)
    #emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)

if __name__ == '__main__':
    #!app.run(debug=True, port=5000)
    socketio.run(app, debug=True)