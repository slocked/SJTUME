from flask import Flask, render_template, session, url_for, flash, request, make_response  
from flask import make_response
from flask import redirect
import os
import time  
import hashlib  
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
import xml.etree.ElementTree as ET



app=Flask(__name__)  
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = 'GCXDL'



app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'door_state')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)



bootstrap = Bootstrap(app)


door_state={'state':0}


class DOOR(db.Model):
    __tablename__ = 'doors'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64),unique = False, index=True)

    def __init__(self, u):
        self.username = u

    def __repr__(self):
        return '<Door %r User %r>' % (self.id, self.username)



db.create_all()
door_1 = DOOR('NULL')
door_2 = DOOR('NULL')

db.session.add(door_1)
db.session.add(door_2)
db.session.commit()


@app.route('/',methods=['GET','POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you changed your name!')
        session['name']=form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html',form=form, name=session.get('name'))



@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)



@app.route('/open',methods=['GET','POST'])
def open():
    form = DoorForm()
    if form.validate_on_submit():
        door_state['state'] = form.name.data
        form.name.data = ''
        return redirect(url_for('open'))
    return render_template('openDoor.html',form=form)


@app.route('/session',methods=['GET','POST'])
def test():
    return render_template('door_state.html',door_state=door_state['state'])

@app.route('/door')
def door():
    door1 = DOOR.query.filter_by(id=1).first()
    door2 = DOOR.query.filter_by(id=2).first()
    if door1.username == "NULL":
        door1_state = 'N'
    else:
        door1_state = 'Y'

    if door2.username == "NULL":
        door2_state = 'N'
    else:
        door2_state = 'Y'
        
    return render_template('door_state.html',door_state=("["+door1_state+"]["+door2_state+"]"))



@app.route('/doorpy')
def doorpy():
	door1 = DOOR.query.filter_by(id=1).first()
	door2 = DOOR.query.filter_by(id=2).first()
	if door1.username == "NULL":
		door1_state = 'N'
	else:
		door1_state = 'Y'
	if door2.username == "NULL":
		door2_state = 'N'
	else:
		door2_state = 'Y'
	return render_template('doorpy.html',d1=door1_state,d2=door2_state)




@app.route('/wechat', methods = ['GET', 'POST'] )  
def wechat_auth():  
  global response
  if request.method == 'GET':
    token = 'gcxdl'  
    query = request.args  # GET 方法附上的参数  
    signature = query.get('signature', '')  
    timestamp = query.get('timestamp', '')  
    nonce = query.get('nonce', '')  
    echostr = query.get('echostr', '')  
    s = [timestamp, nonce, token]  
    s.sort()  
    s = ''.join(s)  
    if ( hashlib.sha1(s).hexdigest() == signature ):    
       return make_response(echostr)  

  else :
    rec = request.stream.read()
    xml_rec = ET.fromstring(rec)
    msgtype = xml_rec.find('MsgType').text
    to_usr = xml_rec.find('ToUserName').text
    from_usr = xml_rec.find('FromUserName').text
    xml_rep_text = "<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[text]]></MsgType><Content>%s</Content></xml>"
    if msgtype == "event":
        msgcontent = xml_rec.find('Event').text
        eventk = xml_rec.find('EventKey').text

        if msgcontent == "subscribe":
            msgcontent = "【工导测试公众号】 欢迎使用智能柜系统，您可以通过底部菜单栏按钮存取物品，课程网站菜单内有我们组的自建网站及项目源码，智能家居接口正在开发中，感谢您的关注。"
            response = make_response(xml_rep_text % (from_usr,to_usr,str(int(time.time())),msgcontent))
            response.content_type='application/xml'
            return response

        if msgcontent == "LOCATION":
            latitude = xml_rec.find('Latitude').text
            longtitude = xml_rec.find('Longitude').text
            precision = xml_rec.find('Precision').text
            msgcontent = "Latitude: %s ; Longtitude: %s ; Precision: %s " % (latitude,longtitude,precision)
            response = make_response(xml_rep_text % (from_usr,to_usr,str(int(time.time())),msgcontent))
            response.content_type='application/xml'
            return response

        if msgcontent == "CLICK" and eventk == "deposit":
            find = DOOR.query.filter(DOOR.username != "NULL").all()
            l = len(find)
            flag = False
            i=0
            while i <= l-1:
                if from_usr in find[i].username:
                    flag= True
                i += 1
            if flag:
                msgcontent = "抱歉，您有已存的物品，请先取出"
                response = make_response(xml_rep_text % (from_usr,to_usr,str(int(time.time())),msgcontent))
                response.content_type='application/xml'
                return response
            else:
                find = DOOR.query.filter(DOOR.username == "NULL").all()
                l = len(find)
                if l == 0:
                    msgcontent = "抱歉，储物柜已满"
                    response = make_response(xml_rep_text % (from_usr,to_usr,str(int(time.time())),msgcontent))
                    response.content_type='application/xml'
                    return response
                else:
                    response = make_response(xml_rep_text % (from_usr,to_usr,str(int(time.time())),msgcontent))
                    find = DOOR.query.filter(DOOR.username == "NULL").first()
                    find.username = from_usr
                    msgcontent = "正在为您打开 %s 号柜" % find.id
                    db.session.add(find)
                    response = make_response(xml_rep_text % (from_usr,to_usr,str(int(time.time())),msgcontent))
                    response.content_type='application/xml'
                    return response

        if msgcontent == "CLICK" and eventk == "retrieve":
            find = DOOR.query.filter_by(username=from_usr).first()
            if find == None:
                msgcontent = "系统检测到您没有已存的物品"
                response = make_response(xml_rep_text % (from_usr,to_usr,str(int(time.time())),msgcontent))
                response.content_type='application/xml'
                return response
            else:
                msgcontent = "回复 1 确认打开您已存的柜子"
                response = make_response(xml_rep_text % (from_usr,to_usr,str(int(time.time())),msgcontent))
                response.content_type='application/xml'
                return response

    if msgtype == "text":
        msgcontent = xml_rec.find('Content').text

        if msgcontent == "1":
            find = DOOR.query.filter_by(username=from_usr).first()
            num = find.id
            msgcontent = '确认成功，正在为您打开 %s 号柜' % num
            find.username='NULL'
            db.session.add(find)
            response = make_response(xml_rep_text % (from_usr,to_usr,str(int(time.time())),msgcontent))
            response.content_type='application/xml'
            return response
        else:
            msgcontent = "?"
            response = make_response(xml_rep_text % (from_usr,to_usr,str(int(time.time())),msgcontent))
            response.content_type='application/xml'
            return response





class NameForm(Form):
    name=StringField('your name please',validators=[Required()])
    submit = SubmitField('提交用户名')

class DoorForm(Form):
    name=StringField('请输入柜子编号：',validators=[Required()])
    submit = SubmitField('确认')





if __name__ == '__main__':  
    app.run()