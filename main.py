from flask import Flask, render_template, request, redirect, url_for, session, flash
import csv
from datetime import datetime
import sys

app = Flask(__name__)
app.secret_key = 'some_secret'
login_file_path = 'user_database.csv'
lundary_file_path = 'lundary_database.csv'

def add_user(id_data,pw_data): #return value : Error message / False
    new_user = [id_data,pw_data]

    with open(login_file_path, 'r', newline='') as file:
        csv_reader = csv.reader(file)
        id_list = [row[0] for row in csv_reader]

    with open(login_file_path, 'a', newline='') as file:
        csv_writer = csv.writer(file)
        if id_data in id_list:
            return False
        else:
            csv_writer.writerow(new_user)
            return True
        
def user_login(id_data,pw_data): #return value : Error message / False
    with open(login_file_path, 'r', newline='') as file:
        csv_reader = csv.reader(file)

        for row in csv_reader:
            if row[0] == id_data:
                if row[1] == pw_data:
                    return True
        return False

def init_laundry():
    with open(lundary_file_path, 'w', newline='') as file:
        csv_writer = csv.writer(file)

        row = [None,None,None]
        for i in range(12):
            row[0]=i
            csv_writer.writerow(row)

def start_use(machine,id_data,start_time): #machine은 숫자로 관리함.
    data = []
    with open(lundary_file_path, 'r', newline='') as file:
        csv_reader = csv.reader(file)

        for row in csv_reader:
            if int(row[0]) ==  machine:
                row[1] = id_data
                row[2] = start_time
            data.append(row)

    with open(lundary_file_path, 'w', newline='') as file:
        csv_writer = csv.writer(file)

        for row in data:
            csv_writer.writerow(row)

def check_end_use(): #machine은 숫자로 관리함.
    strformat ='%Y-%m-%d %H:%M:%S.%f'
    data = []
    with open(lundary_file_path, 'r', newline='') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            data.append(row)

    with open(lundary_file_path, 'w', newline='') as file:
        csv_writer = csv.writer(file)
        for row in data:
            if row[2]:
                if (datetime.now()-datetime.strptime(row[2],strformat)).total_seconds() > 50*60:
                    row[1] = None
                    row[2] = None
            csv_writer.writerow(row)
            

def time_left():
    strformat ='%Y-%m-%d %H:%M:%S.%f'
    time_list = []
    with open(lundary_file_path, 'r', newline='') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if row[2] != '':
                time_list.append(50-(datetime.now()-datetime.strptime(row[2],strformat)).total_seconds()/60)
            else:
                time_list.append('사용가능')
    return time_list

def who_occupied(): #
    user_list = []
    with open(lundary_file_path, 'r', newline='') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if row[1] != '':
                user_list.append(row[1])
            else:
                user_list.append(None)
    return user_list

init_laundry()

@app.route('/',methods = ['POST','GET'])
def main_page():
    check_end_use()
    timelist = time_left()
    userlist = who_occupied()
    if request.method == 'POST':
        return redirect(url_for(("login")))
    else:
        return render_template('index.html', lundata = timelist)

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
    if request.method == 'POST':
        room = request.form['room_number']
        password = request.form['password']
        if user_login(room,password):
            return redirect(url_for(("main_page")))
        else:
            flash("잘못된 호수, 비밀번호입니다.")
            return render_template("login.html")
    else:    
        return render_template("login.html")

@app.route('/using' , methods = ["POST","GET"])
def using():

    lundary_number = request.args.get('lnum', "lundary_number_fail")
    user = request.args.get('user', "user_fail")
    start_time = str(datetime.now())
    start_use(int(lundary_number),user,start_time)
    #http://127.0.0.1:5000/using?lnum=1&user=708
    return redirect(url_for(("main_page")))

@app.route('/chat' , methods = ["POST","GET"])
def chatting():
    lundary_number = request.args.get('lnum', "lundary_number_fail")
    print(lundary_number)
    #http://127.0.0.1:5000/using?lnum=4&user=708
    return render_template("chat.html", lnum = lundary_number)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(sys.argv[1]))