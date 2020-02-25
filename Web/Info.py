# encoding:utf-8

import sqlite3
import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './static/equipmentFiles/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
keyWords = {'All': 0, '关键词': 1, '购买自（公司）': 'institution', '设备类型': 'category', '购买人': 'Purchaser', '购买时间（格式：2020-01-01---2020-02-01）': 5,}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

@app.route('/index')
@app.route('/')
def index():
    return render_template('./index.html')

@app.route('/subscribe_article')
def subscribe_article():
    return render_template('./subscribe_article.html')

@app.route('/input')
def input():
    return render_template('./input.html')

@app.route('/query_web')
def query_web():
    return render_template('./query.html')

@app.route('/success/<name>')
def success(name):
   return 'welcome %s !' % name

@app.route('/delete/<name>')
def delete(name):
   return '%s have deleted your information !' % name

@app.route('/sucessSubmit')
def sucessSubmit():
   return 'You have successed submit the information !'

@app.route('/notFind')
def notFind():
   return "Sorry, There's nothing here for you !"

@app.route('/submit_info',methods = ['POST', 'GET'])
def submit_info():

    user = request.form['name']

    database = '../DataBase/personQueryInfo.db'
    conn = sqlite3.connect(database)
    c = conn.cursor()

    try:
        c.execute('''create table user_tb(
            _id integer primary key autoincrement,
            keyWords text,
            authors text,
            email text,
            person text,
            company text,
            major text)
            ''')
    except:
        pass

    c.execute('insert into user_tb values(null, ?, ?, ?, ?, ?, ?)',
                ((request.form['keywords'], request.form['author'], request.form['email'], \
                    request.form['name'], request.form['institution'], request.form['article'])))

    conn.commit()

    c.close()
    conn.close()

    return redirect(url_for('success',name = user))

@app.route('/delete_info',methods = ['POST', 'GET'])
def delete_info():

    user = request.form['delName']
    email = request.form['delEmail']

    database = '../DataBase/personQueryInfo.db'
    conn = sqlite3.connect(database)
    c = conn.cursor()

    c.execute("delete from user_tb where email = '{}'".format(email))
    conn.commit()
    c.close()
    conn.close()

    return redirect(url_for('delete',name = user))

@app.route('/delete_equipments',methods = ['POST','GET'])
def delete_equipments():

    option = request.form['option']
    ID = request.form['ID']
    number = request.form['number']

    database = '../DataBase/equipmentInfo.db'
    conn = sqlite3.connect(database)
    c = conn.cursor()
    sql = ''' UPDATE user_tb SET number = ? WHERE _id = ?'''

    if option == 'd':
        print('ok')
        c.execute("delete from user_tb where _id = '{}'".format(ID))
    elif option == 'p':
        c.execute("select number from user_tb where _id = '{}'".format(ID))
        rows = c.fetchall()
        new_number = int(rows[0][0])+int(number)
        c.execute(sql, (new_number,ID))
    elif option == 'm':
        c.execute("select number from user_tb where _id = '{}'".format(ID))
        rows = c.fetchall()
        new_number = int(rows[0][0])-int(number)
        if new_number<0:
            new_number = 0
        c.execute(sql, (new_number,ID))


    conn.commit()
    c.close()
    conn.close()

    return render_template('./query.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files.getlist("file")
        fileFig = file[0]
        urlFig = UPLOAD_FOLDER+fileFig.filename
        if len(file)>1:
            fileFile = file[1]
            urlFile = UPLOAD_FOLDER+fileFile.filename
        else:
            fileFile = False
            urlFile = UPLOAD_FOLDER

        # if user does not select file, browser also
        # submit an empty part without filename
        if fileFig.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if fileFig and allowed_file(fileFig.filename):
            filename = secure_filename(fileFig.filename)
            fileFig.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        if fileFile and allowed_file(fileFile.filename):
            filename = secure_filename(fileFile.filename)
            fileFile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    database = '../DataBase/equipmentInfo.db'
    conn = sqlite3.connect(database)
    c = conn.cursor()

    try:
        c.execute('''create table user_tb(
            _id integer primary key autoincrement,
            equName text,
            equInfo text,
            category text,
            institution text,
            number text,
            Purchaser text,
            time date,
            Figure text,
            file text)
            ''')
    except:
        pass

    c.execute('insert into user_tb values(null, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                ((request.form['equName'], request.form['equInfo'], request.form['category'], \
                    request.form['institution'], request.form['number'], request.form['Purchaser'], \
                        request.form['time'], urlFig, urlFile)))

    conn.commit()

    c.close()
    conn.close()


    return redirect(url_for('sucessSubmit'))

@app.route('/query', methods=['GET', 'POST'])
def query():
    classes = keyWords[request.form['category']]
    keywords = request.form['keywords']

    if classes == 0:
        info = query_info(classes, keywords)
    
    # 关键词搜索
    elif classes == 1:
        info = query_info(classes, keywords)

    # 时间范围搜索
    elif classes == 5:
        startTime = keywords[:10]
        stopTime = keywords[13:]
        info = query_info(classes, (startTime, stopTime))

    # 其他搜索
    else:
        info = query_info(classes, keywords)

    if len(info) == 0:
        return redirect(url_for('notFind'))

    length = len(info)
    return render_template('./display_query.html', info=info, length=length)

def is_contain_chinese(check_str):
    """
    判断字符串中是否包含中文
    :param check_str: {str} 需要检测的字符串
    :return: {bool} 包含返回True， 不包含返回False
    """
    for ch in check_str:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False

def query_info(classes, keys):

    database = '../DataBase/equipmentInfo.db'
    conn = sqlite3.connect(database)
    c = conn.cursor()
    info = []
    try:
        if classes == 0:
            c.execute("select * from user_tb")
        elif classes == 1:
            c.execute("select * from user_tb where equName like '%{}%' or equInfo like '%{}%'".format(keys, keys))
        elif classes == 5:
            c.execute("select * from user_tb where time >= '{}' and time <= '{}'".format(keys[0], keys[1]))
        else:

            if is_contain_chinese(classes) and is_contain_chinese(keys):
                c.execute("select * from user_tb where '{}' = '{}'".format(classes, keys))
            elif is_contain_chinese(classes) and (not is_contain_chinese(keys)):
                c.execute("select * from user_tb where '{}' = {}".format(classes, keys))
            elif (not is_contain_chinese(classes)) and is_contain_chinese(keys):
                c.execute("select * from user_tb where {} = '{}'".format(classes, keys))
            elif (not is_contain_chinese(classes)) and (not is_contain_chinese(keys)):
                c.execute("select * from user_tb where {} = {}".format(classes, keys))
    except:
        return info
    # id = {}
    # equName = {}
    # equInfo = {}
    # category = {}
    # institution = {}
    # number = {}
    # Purchaser = {}
    # time = {}

    # while True:
    #     row = c.fetchone()
    #     if not row:
    #         break
    #     id[row[0]] = row[0]
    #     equName[row[0]] = row[1]
    #     equInfo[row[0]] = row[2]
    #     category[row[0]] = row[3]
    #     institution[row[0]] = row[4]
    #     number[row[0]] = row[5]
    #     Purchaser[row[0]] = row[6]
    #     time[row[0]] = row[7]

    # info = {'id': id, 'equName': equName, 'equInfo': equInfo, 'category': category, 'institution': institution, 'number': number, \
    #     'Purchaser': Purchaser, 'time': time}

    # 整理info的信息，使得html端容易处理

    while True:
        row = c.fetchone()
        if not row:
            break
        info.append(str(row[0]))
        info.append(row[8])
        info.append(row[1])
        info.append(row[2])
        info.append(row[3])
        info.append(row[4])
        info.append(row[5])
        info.append(row[6])
        info.append(row[7])

    return info

if __name__ == '__main__':
   app.run(debug = True)