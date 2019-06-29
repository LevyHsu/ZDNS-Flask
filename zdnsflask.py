from flask import Flask, render_template, url_for, request, redirect, send_from_directory
#from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
import random
import os
import time
import subprocess
import demjson

#executor = ProcessPoolExecutor(1)
executor = ThreadPoolExecutor(1)
app = Flask(__name__)

GOPATH = "/usr/bin/go"
ZDNSPATH = "/usr/local/go/bin/bin/./zdns"

loginusername = 'admin'
loginpassword = 'Gk2Lx&tZ7CfZ#QgLJ#EK4S?sR7Spj9_R'
setkey = '_Z%_5T@8_&mDHxxN^GEFuHSnVQRS3jm$K4H?rQ4^amAe7Ekx=Cdz4bC@u*T9^w&H'
sessionkey_global = ''
queue_list = []
finished_list = []

zdns_running = False

@app.route('/')
def hello_world():
    return redirect('/login')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/user/redirect', methods=['POST'])
def redirect_to_new_url():
    if (request.form['username'] == loginusername and request.form['password'] == loginpassword):
        global sessionkey_global
        sessionkey_global = "".join(random.sample(setkey,64 ))
        return redirect(url_for('index',sessionkey=sessionkey_global))
    return redirect('/login')

@app.route('/index/<sessionkey>')
def index(sessionkey):
    if (sessionkey != sessionkey_global):
        return render_template('unauthorized.html')
    global zdns_running
    if not zdns_running:
        zdns_running = True
        executor.submit(zdns_shell,queue_list,finished_list)
    queue_string = ""
    for i in range(len(queue_list)):
        queue_string += "<b>Domain:</b>&nbsp" + queue_list[i][0]
        queue_string += "&nbsp&nbsp<b>Threads:</b>&nbsp" + queue_list[i][1]
        queue_string += "&nbsp&nbsp<b>Dictionary:</b>&nbsp" + queue_list[i][2]                
        queue_string += "&nbsp&nbsp<b>Status:</b>&nbsp" + queue_list[i][3] + "<br>"
    finished_queue_string = ""
    for i in range(len(finished_list)):
        finished_queue_string += "<b>Domain:</b>&nbsp" + finished_list[i][0]
        finished_queue_string += "&nbsp&nbsp<b>Threads:</b>&nbsp" + finished_list[i][1]
        finished_queue_string += "&nbsp&nbsp<b>Dictionary:</b>&nbsp" + finished_list[i][2]                
        finished_queue_string += "&nbsp&nbsp<b>Status:</b>&nbsp" + finished_list[i][3] + "<br>"
    finished_selection = []
    for i in range(len(finished_list)):
        finished_selection.append(finished_list[i][0])
    return render_template('index.html',existing_queue = queue_string, finished_queue = finished_queue_string,finished_list = finished_selection)

def clean_job():
    global queue_list
    global finished_list
    queue_list.clear()
    finished_list.clear()
    for file in os.scandir("output"):
        if file.name.endswith(".txt"):
            os.unlink(file.path)
    return redirect(url_for('index',sessionkey=sessionkey_global))

@app.route('/submit', methods=['POST'])
def new_job():
    domain = request.form.get("Domain")
    threads = request.form.get("Threads")
    dictionary = request.form.get("Dictionary")
    queue_list.append([domain,threads,dictionary,'Wating'])
    if ( str(request.form.get("cleanup")) == "Clean  Queue"):
        clean_job()
    return redirect(url_for('index',sessionkey=sessionkey_global))



@app.route('/downloads')
def download_file():
    filename_temp = str(request.args.get('select_file')) + ".txt"
    print("Downloading: "filename_temp)
    return send_from_directory(directory="output", filename = filename_temp)

def generate_subdomain_file(domain,dictfile):
    input_file = open("dict/" + dictfile + ".txt", "r")
    output_file = open(dictfile + ".temp", "w")
    for line in input_file:
        line = line.strip('\n')
        output_file.write(line+"."+domain+"\n")
    input_file.close()
    output_file.close()
    return (os.getcwd() + "/" + dictfile + ".temp")

def jsonhandle(domain):
    input_file  = open('temp.out',"r")
    output_file = open("output/" + domain +".txt", "a+")
    for line in input_file:
        js = demjson.decode(line)
        domain = js['name']
        ip = 'NULL'
        if js['status'] == 'NOERROR':
            answers = js['data']['answers']
            for answer in answers:
                if answer['type'] == 'A':
                    name = answer['name']
                    ip = answer['answer']
                    output_file.write(name + " " + ip + "\n")
            answers2 = js['data']['additionals']
            for answer in answers2:
                if answer['type'] == 'A':
                    name = answer['name']
                    ip = answer['answer']
                    output_file.write(name + " " + ip + "\n")
    input_file.close()
    output_file.close()            


def zdns_shell(queue_list,finished_list):
    while(1):
        try:
            if not queue_list:
                print("Empty Queue, ZDNS holding.")
                time.sleep(5)
            else:
                print("ZDNS Running on Job")
                queue_list[0][3] = "Executing"
                
                print("Executing: ",queue_list)
                tempfile_path = generate_subdomain_file(queue_list[0][0],queue_list[0][2])
                subprocess.run([ZDNSPATH, "A", "-input-file", tempfile_path, "-output-file", os.getcwd() + "/" + "temp.out", "-threads", queue_list[0][1]])
                os.remove(tempfile_path)
                jsonhandle(queue_list[0][0])
                os.remove("temp.out")
                queue_list[0][3] = "Finished"
                finished_list.append(queue_list[0])
                del queue_list[0]
        except KeyboardInterrupt:
            quit()
    return 0

if __name__ == '__main__':
    app.debug = False
    app.run(host='0.0.0.0',port=8080)
   