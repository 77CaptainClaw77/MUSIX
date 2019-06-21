from flask import Flask
from flask import request
import yaml
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask_sqlalchemy import SQLAlchemy
import os


app=Flask(__name__)

database_info=yaml.safe_load(open('/home/kumarguru/Documents/Programs/Python/MUSIX/db.yaml'))
app.config['SQLALCHEMY_DATABASE_URI']='mysql+'database_info['driver']+"://"+database_info['username']+":"+database_info['password']+':@'+database_info['host']+'/'+database_info['database']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY']=os.urandom(30)
db=SQLAlchemy(app)

class User(db.Model):
    __tablename__='UserInfo'
    user_id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(30),nullable=False)
    username=db.Column(db.String(30),nullable=False)
    password=db.Column(db.String(100),nullable=False)
    email=db.Column(db.String(30),nullable=False)
    phone=db.Column(db.String(15),nullable=False)
    visibility=db.Column(db.Integer,default=0,nullable=False)

@app.route('/login/',methods=['POST,GET'])
def user_login():
    hashes=User.query.

if __name__=='__main__':
    app.run(port=8081,debug=True)