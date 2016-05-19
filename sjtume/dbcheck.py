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
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'door_state')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)

class DOOR(db.Model):
    __tablename__ = 'doors'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64),unique = False, index=True)

    def __init__(self, u):
        self.username = u

    def __repr__(self):
        return '<Door %r User %r>' % (self.id, self.username)

find = DOOR.query.filter(DOOR.username != "NULL").all()

l = len(find)
flag = False
i=0
while i <= l-1:
    if 'joe' in find[i].username:
        flag= True
    i += 1

print(flag)
print(find)
print(len(find))

print(type(find))

#print(find[1].User)

