from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response, jsonify
import csv
from datetime import datetime
import sys

app = Flask(__name__)

app.secret_key = 'some_secret'
login_file_path = 'user_database.csv'
lundary_file_path = 'lundary_database.csv'
chat_file_path = 'chat_database.csv'

chat_item = ['세탁물을 꺼내놓겠습니다.','세탁에 이상이 있습니다.','세탁물이 남아있습니다.','방문 부탁 드립니다.','표시할 메시지가 없습니다.']

def typetrans(time): #str to datetime type
    strformat ='%Y-%m-%d %H:%M:%S.%f'
    return datetime.strptime(time, strformat)

def left_time_50(time): #datetime type
    time_diff = 50*60-int((datetime.now()-time).total_seconds())
    minuite = time_diff//60
    second = time_diff%60

    return minuite, second

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
                    row[2] = ''
            csv_writer.writerow(row)      

def time_left():
    time_list = []
    with open(lundary_file_path, 'r', newline='') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if row[2] != '':
                time = typetrans(row[2])
                minute,second = left_time_50(time)
                time_list.append(f"{minute}분 {second}초 남음")
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

def init_chat():
    with open(chat_file_path, 'a', newline='') as file:
        pass

def make_chat(sender,reciever,message):
    data = []
    with open(chat_file_path, 'r', newline='') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            data.append(row)
        data.append([sender,reciever,message,datetime.now()])

    with open(chat_file_path, 'w', newline='') as file:
        csv_writer = csv.writer(file)
        for row in data:
            csv_writer.writerow(row)

def check_chat(reciever): #나에게로 온 채팅 return
    sender = ''
    message = ''

    data = []
    sent_me_chats = []
    
    with open(chat_file_path, 'r', newline='') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if row[1] == reciever:
                sender = row[0]
                message = row[2]
                
                time = typetrans(row[3])
                send_time = ''
                time_component = left_time_chat(time)
                for item in time_component:
                    send_time += item
                send_time += ' 전에 보냄'

                sent_me_chats.append([sender, int(message), send_time])

            data.append(row)

    
    with open(chat_file_path, 'w', newline='') as file:
        csv_writer = csv.writer(file)
        for row in data:
            csv_writer.writerow(row)

    if sent_me_chats:
        return sent_me_chats
    else:
        return [['',4,'']]

def typetrans(time): #str to datetime type
    strformat ='%Y-%m-%d %H:%M:%S.%f'
    return datetime.strptime(time, strformat)

def left_time_chat(time): #datetime type
    time_diff = int((datetime.now()-time).total_seconds())
    date = time_diff // (3600*60*24)
    hour = (time_diff - date*3600*60*24) // 3600
    minute = (time_diff-3600*hour- date*3600*60*24)//60
    #second = (time_diff-3600*hour)%60
        
    return [f'{hour}시간', f'{minute}분']

init_laundry()

@app.route('/',methods = ['POST','GET'])
def main_page():
    if request.cookies.get('loginid'):
        check_end_use()
        ids = request.cookies.get('loginid')
        chatlist = check_chat(ids)
        chatlist[-1][1] = chat_item[int(chatlist[-1][1])]
        timelist = time_left()
        if request.method == 'POST':
            return redirect(url_for(("login")))
        if chatlist != []:
            return render_template('index.html', lundata = timelist , id = '환영합니다 ' +ids +'호 님' , chat = chatlist)
        else:
            return render_template('index.html', lundata = timelist , id = '환영합니다 ' +ids +'호 님' , chat = [["받은"],["메시지"],["없음"]])

    else:
        return redirect(url_for('login'))

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
            resp = make_response(redirect('/'))
            resp.set_cookie('loginid',room ,domain= 'secondwind-hackerton-bjdzu.run.goorm.io')
            return resp
        else:
            flash("잘못된 호수, 비밀번호입니다.")
            return render_template("login.html")
    elif request.method == 'MOVE':
        return redirect(url_for(("register")))
    else:    
        return render_template("login.html")

@app.route('/using' , methods = ["POST","GET"])
def using():
    lundary_number = request.args.get('lnum', "lundary_number_fail")
    user = request.cookies.get('loginid')
    start_time = str(datetime.now())
    start_use(int(lundary_number),user,start_time)
    #http://127.0.0.1:5000/using?lnum=1&user=708
    return redirect(url_for(("main_page")))

@app.route('/chat' , methods = ["POST","GET"])
def chatting():
    lundary_number = request.args.get('lnum', "lundary_number_fail")
    return render_template('chat.html',lunnum = lundary_number)
    
@app.route('/chatdatainput' , methods = ["POST","GET"])
def chatdata():
    lundary_number = request.args.get('lnum', "lundary_number_fail")
    msg = request.args.get('msg', "msg_fail")
    #http://127.0.0.1:5000/using?lnum=1&user=708
    if msg != 'msg_fail':
        sender = request.cookies.get('loginid')

        pre_user = who_occupied()[int(lundary_number)]
        make_chat(sender,pre_user,msg)
        return redirect(url_for(("main_page")))

if __name__ == '__main__':
    app.run(debug=True)