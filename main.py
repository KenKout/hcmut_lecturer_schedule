import json
import time
from flask import Flask, request
from flask_cors import CORS  # The typical way to import flask-cors
import threading
import os
start_time = time.time()
name_teacher = []
teacher_info = []
f = open('data.json')
data = json.load(f)

f = open('data_lecturer.json')
data_lecturer = json.load(f)
def search_by_maMonHoc(data,maMonHoc):
    for i in data:
        if i['maMonHoc'].lower() == maMonHoc.lower():
            return i
    return {}
def search_by_giangVien(data,giangVien):
    data_return = []
    if type(data) == dict:
        data = [data]
    for i in data:
        json_data = i.copy()
        json_data['lichHoc'] = []
        for j in i['lichHoc']:
            if j['giangVien'].lower() == giangVien.lower() or j['giangVienBT'].lower() == giangVien.lower():
                json_data['lichHoc'].append(j)
        if len(json_data['lichHoc']) > 0:
            data_return.append(json_data)
    return data_return
def search_info_lecturer(data_lecturer,giangVien):
    for i in data_lecturer:
        if i['name'].lower() == giangVien.lower():
            return i
    return {}

def return_teacher_name(data):
    global name_teacher
    global teacher_info
    for i in data:
        for j in i['lichHoc']:
            if j['giangVien'] not in name_teacher and j['giangVienBT'] not in name_teacher:
                name_teacher.append(j['giangVien'])
                name_teacher.append(j['giangVienBT'])
            elif j['giangVien'] not in name_teacher:
                name_teacher.append(j['giangVien'])
            elif j['giangVienBT'] not in name_teacher:
                name_teacher.append(j['giangVienBT'])
    for i in name_teacher:
        teacher_info.append(search_info_lecturer(data_lecturer,i) if search_info_lecturer(data_lecturer,i) != {} else {'name':i,'phone':'','email':''})
FlaskApp = Flask(__name__)
cors = CORS(FlaskApp)
@FlaskApp.route('/api')
def WebAPI():
    if "CF-Connecting-IP" in request.headers:
        remote_addr = request.headers.getlist("CF-Connecting-IP")[0].rpartition(' ')[-1]
    elif 'X-Forwarded-For' in request.headers:
        remote_addr = request.headers.getlist("X-Forwarded-For")[0].rpartition(' ')[-1]
    else:
        remote_addr = request.remote_addr or 'untrackable'
    maMonHoc = request.args.get('id')
    giangVien = request.args.get('gv')
    if maMonHoc != None and giangVien != None:
        print(f"request from {remote_addr} with id={maMonHoc} and gv={giangVien}")
        return search_by_giangVien(search_by_maMonHoc(data,maMonHoc),giangVien)
    elif maMonHoc != None:
        print(f"request from {remote_addr} with id={maMonHoc}")
        return search_by_maMonHoc(data,maMonHoc)
    elif giangVien != None:
        print(f"request from {remote_addr} with gv={giangVien}")
        return search_by_giangVien(data_lecturer,giangVien)
    print(f"Invalid request from {remote_addr}")
    return []

@FlaskApp.route('/api/info')
def WebAPI_Info():
    if "CF-Connecting-IP" in request.headers:
        remote_addr = request.headers.getlist("CF-Connecting-IP")[0].rpartition(' ')[-1]
    elif 'X-Forwarded-For' in request.headers:
        remote_addr = request.headers.getlist("X-Forwarded-For")[0].rpartition(' ')[-1]
    else:
        remote_addr = request.remote_addr or 'untrackable'
    giangVien = request.args.get('gv')
    if giangVien != None:
        print(f"request from {remote_addr} with gv={giangVien}")
        return search_info_lecturer(data_lecturer,giangVien)
    else:
        print(f"request from {remote_addr} - Get all info")
        return teacher_info

@FlaskApp.route('/')
def Main():
    return '@KenKout'
def RunWebAPI():
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    FlaskApp.run(port=int(os.environ.get("PORT", 8080)),host='0.0.0.0')


return_teacher_name(data)
threading.Thread(target=RunWebAPI).start()
