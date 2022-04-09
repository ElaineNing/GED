from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'GEDemployee'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddEmp.html')


@app.route("/about", methods=['GET', 'POST'])
def about():
    return render_template('about.html', about=about)


@app.route("/GetEmp", methods=['GET', 'POST'])
def GetEmp():
    return render_template('GetEmp.html', GetEmp=GetEmp)


@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    phone = request.form['phone']
    ot = request.form['ot']
    insurance = request.form['insurance']
    allowance = request.form['allowance']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO GEDemployee VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location, phone, ot, insurance, allowance))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)


@app.route("/fetchdata", methods=['GET', 'POST'])
def fetchdata():
    if request.method == 'POST':
        try:
            emp_id = request.form['emp_id']
            cursor = db_conn.cursor()
            
            fetch_sql = "SELECT * FROM GEDemployee WHERE emp_id = %s"
            cursor.execute(fetch_sql,(emp_id))
            emp = cursor.fetchall()
            
            (emp_id, first_name, last_name, pri_skill, location, phone, ot, insurance, allowance) = emp[0]
             #image_url = show_image(custombucket)#
             
            return render_template('GetEmpOutput.html', emp_id=emp_id, first_name=first_name, last_name=last_name, pri_skill=pri_skill, location=location, phone=phone, ot=ot, insurance=insurance, allowance=allowance)
        except Exception as e:
            return render_template('NotFound.html')
    else:
        return render_template('AddEmp.html', fetchdata=fetchdata)


@app.route("/delete", methods=['GET', 'POST'])
def delete():
    emp_id = request.form['emp_id']
    cursor = db_conn.cursor()
    delete_emp = "DELETE FROM GEDemployee WHERE emp_id = %s"
    cursor.execute(delete_emp, (emp_id))
    db_conn.commit()
    
    
    

