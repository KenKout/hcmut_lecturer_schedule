from flask import Flask,request
from flask_cors import CORS,cross_origin  # The typical way to import flask-cors
import json
import time
import threading
import os

name_teacher = []
teacher_info = []
subject_info = []

current_dir = os.path.dirname(os.path.abspath(__file__))
data_json_path = os.path.join(current_dir, 'data.json')
data_lecturer_json_path = os.path.join(current_dir, 'data_lecturer.json')

with open(data_json_path) as f:
    data = json.load(f)

with open(data_lecturer_json_path) as f:
    data_lecturer = json.load(f)

def convert_vietnamese_to_normal(text):
    # Define a mapping of Vietnamese characters with accents to their normal counterparts
    vietnamese_chars = "ÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ"
    normal_chars = "AAAAAAAAAAAAAAAAAEEEEEEEEEEEIIIIIOOOOOOOOOOOOOOOOOUUUUUUUUUUUYYYYYDaaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyyd"

    # Convert each character in the input text to its normal version
    converted_text = ""
    for char in text:
        if char in vietnamese_chars:
            char_index = vietnamese_chars.index(char)
            char = normal_chars[char_index]
        converted_text += char

    return converted_text



    
def search_by_maMonHoc(data,maMonHoc):
    for i in data:
        if i['maMonHoc'].lower() == maMonHoc.lower():
            for j in i['lichHoc']:
                info_teacher = search_info_lecturer(data_lecturer,j['giangVien'])
                j['email'] = info_teacher['email']
                j['phone'] = info_teacher['phone']
                info_teacher = search_info_lecturer(data_lecturer,j['giangVienBT'])
                j['emailBT'] = info_teacher['email']
                j['phoneBT'] = info_teacher['phone']
            return [i]
    return []
def search_by_giangVien(data,giangVien):
    data_return = []
    if type(data) == dict:
        data = [data]
    for i in data:
        json_data = i.copy()
        json_data['lichHoc'] = []
        for j in i['lichHoc']:
            if convert_vietnamese_to_normal(j['giangVien']).lower() == convert_vietnamese_to_normal(giangVien).lower() or convert_vietnamese_to_normal(j['giangVienBT']).lower() == convert_vietnamese_to_normal(giangVien).lower():
                info_teacher = search_info_lecturer(data_lecturer,j['giangVien'])
                j['email'] = info_teacher['email']
                j['phone'] = info_teacher['phone']
                info_teacher = search_info_lecturer(data_lecturer,j['giangVienBT'])
                j['emailBT'] = info_teacher['email']
                j['phoneBT'] = info_teacher['phone']
                json_data['lichHoc'].append(j)
        if len(json_data['lichHoc']) > 0:
            data_return.append(json_data)
    return data_return
def search_info_lecturer(data_lecturer,giangVien):
    for i in data_lecturer:
        if convert_vietnamese_to_normal(i['name']).lower() == convert_vietnamese_to_normal(giangVien).lower():
            return i
    return {'name':giangVien,'phone':'','email':''}

def return_teacher_name(data):
    global name_teacher
    global teacher_info
    for i in data:
        for j in i['lichHoc']:
            if j['giangVien'] == j['giangVienBT'] and j['giangVien'] not in name_teacher:
                name_teacher.append(j['giangVien'])
            if j['giangVien'] not in name_teacher and j['giangVienBT'] not in name_teacher and j['giangVien'] != j['giangVienBT']:
                name_teacher.append(j['giangVien'])
                name_teacher.append(j['giangVienBT'])
            elif j['giangVien'] not in name_teacher:
                name_teacher.append(j['giangVien'])
            elif j['giangVienBT'] not in name_teacher:
                name_teacher.append(j['giangVienBT'])
    for i in name_teacher:
        teacher_info.append(search_info_lecturer(data_lecturer,i) if search_info_lecturer(data_lecturer,i) != {} else {'name':i,'phone':'','email':''})
        
def return_subject_name(data):
    global subject_info
    for i in data:
        if i['maMonHoc'] not in subject_info:
            subject_info.append({"id":i['maMonHoc'], "name":i['tenMonHoc']})
            
app = Flask(__name__)
cors = CORS(app)

@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/about')
def about():
    return '@KenKout'

@app.route('/api')
def WebAPI():
    if "CF-Connecting-IP" in request.headers:
        remote_addr = request.headers.getlist("CF-Connecting-IP")[0].rpartition(' ')[-1]
    elif 'X-Forwarded-For' in request.headers:
        remote_addr = request.headers.getlist("X-Forwarded-For")[0].rpartition(' ')[-1]
    else:
        remote_addr = request.remote_addr or 'untrackable'
    maMonHoc = request.args.get('id')
    giangVien = request.args.get('gv')
    if maMonHoc != None and giangVien != None and maMonHoc != "" and giangVien != "" :
        print(f"request from {remote_addr} with id={maMonHoc} and gv={giangVien}")
        return search_by_giangVien(search_by_maMonHoc(data,maMonHoc),giangVien)
    elif maMonHoc != None and maMonHoc != "":
        print(f"request from {remote_addr} with id={maMonHoc}")
        return search_by_maMonHoc(data,maMonHoc)
    elif giangVien != None and giangVien != "":
        print(f"request from {remote_addr} with gv={giangVien}")
        return search_by_giangVien(data,giangVien)
    print(f"Invalid request from {remote_addr}")
    return []

@app.route('/api/info')
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

@app.route('/api/info/subject')
def WebAPI_Info_Subject():
    if "CF-Connecting-IP" in request.headers:
        remote_addr = request.headers.getlist("CF-Connecting-IP")[0].rpartition(' ')[-1]
    elif 'X-Forwarded-For' in request.headers:
        remote_addr = request.headers.getlist("X-Forwarded-For")[0].rpartition(' ')[-1]
    else:
        remote_addr = request.remote_addr or 'untrackable'
    print(f"request from {remote_addr} - Get all info")
    return subject_info

def RunWebAPI():
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(port=int(os.environ.get("PORT", 8080)),host='0.0.0.0')
    
return_teacher_name(data)
return_subject_name(data)
RunWebAPI()
