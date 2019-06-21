from flask import Flask
from flask import request
import yaml
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
import os
from flask import url_for
from flask import redirect

app=Flask(__name__)

#database_info=yaml.safe_load(open('/home/kumarguru/Documents/Programs/Python/MUSIX/db.yaml'))
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:@localhost/musicdata'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY']=os.urandom(10)
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

@app.route('/login/',methods=['POST','GET'])
def user_login():
    if request.method=='POST':
        data=User.query.all()
        u_n=request.form['username']
        p=request.form['password']
        #print(data)
        for i in data:
            if i.username==u_n and check_password_hash(i.password,p):
                print(i)
                return redirect(url_for('profile',id=i.user_id))
        return render_template('login.html',data='fail')
    return render_template('login.html',data='no_attempt')

@app.route('/user_profile/<int:id>')
def profile(id):
    return "DONE"

@app.route('/signup/',methods=['POST','GET'])
def sign_up():
    if request.method=='POST':
        n=request.form['name']
        u_n=request.form['uname']
        p=request.form['password']
        em=request.form['email']
        ph=request.form['phone']
        session_a=db.session
        insert_data=User(name=n,username=u_n,password=generate_password_hash(p),email=em,phone=ph)
        try:
            session_a.add(insert_data)
            session_a.commit()
        except:
            session_a.rollback()
            session_a.flush()
        return redirect(url_for('user_login'))
    return render_template('signup.html')
if __name__=='__main__':
    db.create_all()
    app.run(port=8081,debug=True)