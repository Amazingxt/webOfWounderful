from flask import Flask, render_template
import json
import os
 
app = Flask(__name__)
 
testInfo = {}
 
 
@app.route('/test_post/nn', methods=['GET', 'POST'])  # 路由
def test_post():
    testInfo['name'] = 'xiaoliao'
    testInfo['age'] = '28'
    return json.dumps(testInfo)
 
 
@app.route('/')
def hello_world():
    return 'Hello World!'
 
 
@app.route('/index')
def index():
    return render_template('index.html')
 
 
if __name__=="__main__":
    app.run()