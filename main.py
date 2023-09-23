from flask import Flask, render_template, request, redirect, url_for, session, flash
import csv
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'some_secret'
login_file_path = 'database.csv'

def add_user(id_data,pw_data): #return value : Error message / False
    fieldnames = ['User', 'Password']
    new_user = {fieldnames[0]:id_data,fieldnames[1]:pw_data}

    with open(login_file_path, 'r', newline='') as file:
        csv_reader = csv.reader(file)

        id_list = [row[0] for row in csv_reader]

    with open(login_file_path, 'a', newline='') as file:
        csv_writer = csv.writer(file)
        if id_data in id_list:
            return False
        else:
            csv_writer.writerow(new_user.values())
            return True

@app.route('/',methods = ['POST','GET'])
def main_page():
    if request.method == 'POST':
        return redirect(url_for(("login")))
    else:
        return render_template('index.html')

@app.route('/register' , methods = ['POST','GET'])
def register():
    if request.method == 'POST':
        room = request.form['room_number']
        password = request.form['password']
        password_check = request.form['password_check']
        if password_check != password:
            flash("비밀번호가 일치하지 않습니다.")
            return render_template("register.html")
        else:
            if add_user(room,password):
                add_user(room,password)
                return redirect(url_for(("main_page")))
            else:
                flash(f"{room}호 계정은 이미 존재하는 계정입니다.")
                return render_template("register.html")

    else:
        return render_template("register.html")
    
@app.route('/login' , methods = ['POST','GET'])
def login():
    return render_template("login.html")

@app.route('/using' , methods = ["POST","GET"])
def using():

    lundary_number = request.args.get('lnum', "lundary_number_fail")
    user = request.args.get('user', "user_fail")
    start_time = str(datetime.now())

    print(lundary_number,user,start_time)
    #http://127.0.0.1:5000/using?lnum=1234&user=708
    return lundary_number + "-" + user + "-" + start_time

if __name__ == '__main__':
    app.run(debug=True)