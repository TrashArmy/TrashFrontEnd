#!flask/bin/python
from __future__ import print_function
from flask import Flask, xify, abort, request, make_response, url_for
from flask import render_template, redirect


import MySQLdb

import sys

USERNAME = 'root'
PASSWORD = 'password'
DB_NAME = 'DBECE4813'
    
app = Flask(__name__, static_url_path="")

@app.route('/', methods=['GET'])
def home_page():
    conn = MySQLdb.connect (host = "ece4813-rds.cy7xl5j6ypdq.us-east-2.rds.amazonaws.com",
                            user = USERNAME,
                            passwd = PASSWORD,
                            db = DB_NAME, 
                            port = 3306)
    cursor = conn.cursor()
    results =  cursor.fetchall()
    studentlist=[]
    for item in results:
        student={}
        student['ID'] = item[0]
        student['Name'] = item[1]
        student['LastName'] = item[2]
        studentlist.append(student)
    cursor.close()
    conn.close()        
    return render_template('index.html', students=studentlist)

@app.route('/course/viewCourses', methods=['GET'])
def view_courses():
    conn = MySQLdb.connect (    host = "ece4813-rds.cy7xl5j6ypdq.us-east-2.rds.amazonaws.com",
                            user = USERNAME,
                            passwd = PASSWORD,
                            db = DB_NAME, 
                            port = 3306
                        )
    cursor = conn.cursor ()
    cursor.execute("SELECT * FROM Course;");
    results = cursor.fetchall()
    courselist=[]
    for item in results:
        course={}
        course['ID'] = item[0]
        course['Name'] = item[1]
        courselist.append(course)
    cursor.close()
    conn.close()        
    return render_template('viewCourses.html', courses=courselist)

@app.route('/student/fall', methods=['GET'])
def view_fall_students():
    conn = MySQLdb.connect (    host = "ece4813-rds.cy7xl5j6ypdq.us-east-2.rds.amazonaws.com",
                            user = USERNAME,
                            passwd = PASSWORD,
                            db = DB_NAME, 
                            port = 3306
                        )
    cursor = conn.cursor ()
    cursor.execute("SELECT * FROM Takes WHERE semester ='Fall';");
    fallStudents = cursor.fetchall()
    fallList=[]
    for item in fallStudents:
        student_id = item[0]
        cursor.execute("SELECT * FROM Student WHERE sId="+str(student_id)+";")
        results = cursor.fetchall()
        for student in results:
            found = {}
            found['ID'] = student[0]
            found['Name'] = student[1]
            found['LastName'] = student[2]
            fallList.append(found)
    cursor.close()
    conn.close()        
    return render_template('fallStudents.html', students=fallList)

@app.route('/student/spring', methods=['GET'])
def view_spring_students():
    conn = MySQLdb.connect (    host = "ece4813-rds.cy7xl5j6ypdq.us-east-2.rds.amazonaws.com",
                            user = USERNAME,
                            passwd = PASSWORD,
                            db = DB_NAME, 
                            port = 3306
                        )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Takes WHERE semester ='Spring';");
    springStudents = cursor.fetchall()
    springList=[]
    for item in springStudents:
        student_id = item[0]
        cursor.execute("SELECT * FROM Student WHERE sId="+str(student_id)+";")
        results = cursor.fetchall()
        for student in results:
            found = {}
            found['ID'] = student[0]
            found['Name'] = student[1]
            found['LastName'] = student[2]
            springList.append(found)
    cursor.close()
    conn.close()        
    return render_template('springStudents.html', students=springList)


@app.route('/student/add', methods=['GET', 'POST'])
def student_add_page():
    if request.method == 'POST':    
        result = request.form
        conn = MySQLdb.connect (    host = "ece4813-rds.cy7xl5j6ypdq.us-east-2.rds.amazonaws.com",
                            user = USERNAME,
                            passwd = PASSWORD,
                            db = DB_NAME, 
                            port = 3306
                        )
        cursor = conn.cursor()
        statement = "INSERT INTO Student(sId, Name, LastName, Major, GPA) VALUES ("+\
                    request.form['sId']+", '"+\
                    request.form['Name']+"', '"+\
                    request.form['LastName']+"', '"+\
                    request.form['Major']+"', "+\
                    request.form['GPA']+");";
        
        result = cursor.execute(statement);
        
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/')
    else:
        return render_template('add.html')

@app.route('/course/addCourse', methods=['GET', 'POST'])
def class_add_page():
    if request.method == 'POST':    
            result = request.form
            conn = MySQLdb.connect (    host = "ece4813-rds.cy7xl5j6ypdq.us-east-2.rds.amazonaws.com",
                            user = USERNAME,
                            passwd = PASSWORD,
                            db = DB_NAME, 
                            port = 3306
                        )
            cursor = conn.cursor()
            statement = "INSERT INTO Course(cId, cName) VALUES ("+\
                    request.form['cId']+", '"+\
                    request.form['cName']+"');"
            conn.execute(statement)
            conn.commit()
            cursor.close()
            conn.close()
            return redirect('/')
    else:
        return render_template('addCourse.html')


@app.route('/student/delete/<int:student_id>', methods=['GET'])
def delete_student_process(student_id):
    
    conn = MySQLdb.connect (    host = "ece4813-rds.cy7xl5j6ypdq.us-east-2.rds.amazonaws.com",
                            user = USERNAME,
                            passwd = PASSWORD,
                            db = DB_NAME, 
                            port = 3306
                        )
    cursor = conn.cursor()
    results = cursor.execute("DELETE FROM Student WHERE sId="+str(student_id)+";");
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/')

@app.route('/student/update/<int:student_id>', methods=['GET','POST'])
def student_update(student_id):
    if request.method == 'GET':
        conn = MySQLdb.connect (    host = "ece4813-rds.cy7xl5j6ypdq.us-east-2.rds.amazonaws.com",
                            user = USERNAME,
                            passwd = PASSWORD,
                            db = DB_NAME, 
                            port = 3306
                        )
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Student;");
    results = cursor.fetchall()
        student={}
        for item in results:
            if(item[0] == student_id):
                student['ID'] = item[0]
                student['Name'] = item[1]
                student['LastName'] = item[2]
                student['Major'] = item[3]
                student['GPA'] = item[4]
        conn.commit()
        cursor.close()
        conn.close()
        return render_template('updateStudent.html',currentStudent = student)
    else:
        conn = MySQLdb.connect (    host = "ece4813-rds.cy7xl5j6ypdq.us-east-2.rds.amazonaws.com",
                            user = USERNAME,
                            passwd = PASSWORD,
                            db = DB_NAME, 
                            port = 3306
                        )
        cursor = conn.cursor()
        statement = "UPDATE Student SET Name = '" + request.form['Name'] +\
                    "', LastName = '" + request.form['LastName'] +\
                    "', Major = '" + request.form['Major'] +\
                    "', GPA = " + request.form['GPA'] +\
                    " WHERE sId = '" + str(student_id) + "';"
        cursor.execute(statement);
        conn.commit();
        cursor.close();
        conn.close()
        return redirect('/')

@app.route('/student/filter', methods=['GET','POST'])
def student_filter():
    if request.method == 'GET':
        return render_template('filter.html')
    else:
        conn = MySQLdb.connect (    host = "ece4813-rds.cy7xl5j6ypdq.us-east-2.rds.amazonaws.com",
                            user = USERNAME,
                            passwd = PASSWORD,
                            db = DB_NAME, 
                            port = 3306
                        )
        cursor = conn.cursor()
        if(request.form['Semester'] == 'Fall'):
            cursor.execute("SELECT * FROM Takes WHERE semester ='Fall' AND year=" + request.form['Year'] + ";");
        filterEntries = cursor.fetchall()
        else:
            cursor.execute("SELECT * FROM Takes WHERE semester ='Spring' AND year=" + request.form['Year'] + ";");
            filterEntries = cursor.fetchall()
        studentIds=[]
        for item in filterEntries:
            studentIds.append(item[0])

        students = []
        for number in studentIds:
            print(number)
            cursor.execute("SELECT * FROM Student WHERE sId="+str(number)+";")
            results = cursor.fetchall()
            for student in results:
                found = {}
                print(student[0])
                found['ID'] = student[0]
                found['Name'] = student[1]
                found['LastName'] = student[2]
                students.append(found)
        cursor.close()
        conn.commit();
        conn.close();
        return render_template('filterResults.html', students = students)

@app.route('/student/enroll/<int:course_id>', methods=['GET', 'POST'])
def enroll_student_process(course_id):
    if request.method == 'POST':  
        conn = MySQLdb.connect (    host = "ece4813-rds.cy7xl5j6ypdq.us-east-2.rds.amazonaws.com",
                            user = USERNAME,
                            passwd = PASSWORD,
                            db = DB_NAME, 
                            port = 3306
                        )
        cursor = conn.cursor()
        statement = "INSERT INTO Takes VALUES ("+\
            request.form['sId']+", "+\
            str(course_id)+", '"+\
            request.form['semester']+"', "+\
            request.form['year']+");";
        #query = 'INSERT INTO Takes VALUES {} {} {} {}'.format(request.form['sId'],course_id,request.form['semester'],request.form['year'])
        cursor.execute(statement)
    #cursor.execute('INSERT INTO Takes VALUES (%,%,%,%)', (request.form['sId'],course_id,request.form['semester'],request.form['year']))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/')
    else:
        return render_template('enrollStudent.html',course_id= course_id)


@app.route('/student/details/<int:student_id>', methods=['GET'])
def student_details(student_id):
    conn = MySQLdb.connect (host = "ece4813-rds.cy7xl5j6ypdq.us-east-2.rds.amazonaws.com",
                            user = USERNAME,
                            passwd = PASSWORD,
                            db = DB_NAME, 
                            port = 3306
                        )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student;");
    results = cursor.fetchall()
    student={}
    for item in results:
        if(item[0] == student_id):
            student['ID'] = item[0]
            student['Name'] = item[1]
            student['LastName'] = item[2]
            student['Major'] = item[3]
            student['GPA'] = item[4]
    conn.commit()
    cursor.close()
    conn.close()
    return render_template('studentDetails.html',currentStudent = student)

if __name__ == '__main__':
 app.run(host='0.0.0.0', port=80)