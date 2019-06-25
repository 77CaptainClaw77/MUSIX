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
from werkzeug.utils import secure_filename
#from sqlalchemy.orm import relationship

allowed_music_file_types=['wav','mp3','m4a','wma']
allowed_image_files_types=['jpeg','jpg','png']

default_album_image_path=''
default_artist_image_path=''

app=Flask(__name__)

uploads_path='./static/music'

#database_info=yaml.safe_load(open('/home/kumarguru/Documents/Programs/Python/MUSIX/db.yaml'))
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:@localhost/musicdata'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY']=os.urandom(10)
app.config['UPLOAD_FOLDER']=uploads_path
db=SQLAlchemy(app)

#User Database
#-----------------------------------------------------------------------------------------
class User(db.Model):
    __tablename__='UserInfo' 
    user_id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(30),nullable=False)
    username=db.Column(db.String(30),nullable=False)
    password=db.Column(db.String(100),nullable=False)
    email=db.Column(db.String(30),nullable=False)
    phone=db.Column(db.String(15),nullable=False)
    favourites_list=db.Column(db.String(500),nullable=True)# holds ids of users favourite songs
    visibility=db.Column(db.Integer,default=0,nullable=False)
    profile_picture=db.Column(db.String(50),default='Default',nullable=False)
#--------------------------------------------------------------------------------------------

#Music Databse
#-------------------------------------------------------------------------------------------
class Music(db.Model):
    __tablename__='MusicInfo'
    song_id=db.Column(db.Integer,primary_key=True)
    song_name=db.Column(db.String(30),nullable=False)
    song_path=db.Column(db.String(100),nullable=False)
    artist=db.relationship('Artist',backref='music',uselist=False)
    album=db.relationship('Album',backref='music',uselist=False)
#--------------------------------------------------------------------------------------------
#Artist 
#--------------------------------------------------------------------------------------------
class Artist(db.Model):
    __tablename__='ArtistInfo'
    artist_id=db.Column(db.Integer,primary_key=True)
    artist_name=db.Column(db.String(40),nullable=False,default='Unknown')
    artist_image_path=db.Column(db.String(100),nullable=False,default='Path-To-File')
    song_id=db.Column(db.Integer,db.ForeignKey(Music.song_id))
#Album Database
#--------------------------------------------------------------------------------------------
class Album(db.Model):
    __tablename__='AlbumInfo'
    album_id=db.Column(db.Integer,primary_key=True)
    album_name=db.Column(db.String(30),nullable=False,default='Unknown')
    album_cover_image_path=db.Column(db.String(100),nullable=False,default='Path-To-File')
    song_id=db.Column(db.Integer,db.ForeignKey(Music.song_id))    
#--------------------------------------------------------------------------------------------

#Login Functionality
#---------------------------------------------------------------------------------------------
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
#------------------------------------------------------------------------------------------------

#Profile Page
#------------------------------------------------------------------------------------------------
@app.route('/user_profile/<int:id>')
def profile(u_id):
    try:
        profile_data=User.query.filter_by(user_id=u_id).first()
        return render_template('profile.html',data=profile_data)
    except:
        return 'ERROR PROFILE NOT FOUND'
#------------------------------------------------------------------------------------------------

#Signup Page
#------------------------------------------------------------------------------------------------
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

#Edit Profile
# ---------------------------------------------------------------------------------------------
#@app.route('/edit_profile/<int:uid>',methods=['POST','GET'])
#def edit_profile(uid):
    #Edit Logic Here
#----------------------------------------------------------------------------------------------
def file_validate(fname,ftype):
    if fname=='':
        return False
    if ftype=='music':
        if '.' in fname and fname.rsplit('.',1)[1].lower() in allowed_music_file_types:
            return True
    elif ftype=='image':
        if '.' in fname and fname.rsplit('.',1)[1].lower() in allowed_image_files_types:
            return True
    else:
        return False
    return False
#Upload Music
#----------------------------------------------------------------------------------------------
@app.route('/upload_music/',methods=['POST','GET'])
def upload_song():
    if request.method=='POST':
        song_path=""
        song_name=request.form['song_name']
        artist_name=request.form['artist_name']
        album_name=request.form['album_name']
        if 'song_input' not in request.files or song_name=='':
            #No file part in request
            return render_template('music_upload.html',data={'error':'No music file uploaded'})
        s_file=request.files['song_input']
        if s_file and file_validate(s_file.filename,'music'):
            song_fname=secure_filename(s_file.filename)
            s_file.save(os.path.join(app.config['UPLOAD_FOLDER'],song_fname))
            song_path=os.path.join(app.config['UPLOAD_FOLDER'],song_fname)
        else:
            return render_template('music_upload.html',data={'error':'Incorrect format of music file uploaded'})
        album_path=""
        artist_path=""
        
        if "artist_image_input" not in request.files:
            artist_path=default_artist_image_path
        else:
            artist_img_file=request.files['artist_image_input']
            if artist_img_file and file_validate(artist_img_file.filename,'image'):
                artist_fname=secure_filename(artist_img_file.filename)
                artist_img_file.save(os.path.join('./static/img/artist',artist_fname))
                artist_path=os.path.join('./static/img/artist',artist_fname)
            else:
                return render_template('music_upload.html',data={'error':'Incorrect format of image file uploaded'})
        if "album_image_input" not in request.files:
            album_path=default_album_image_path
        else:
            album_img_file=request.files['artist_image_input']
            if album_img_file and file_validate(album_img_file.filename,'image'):
                album_fname=secure_filename(album_img_file.filename)
                album_img_file.save(os.path.join('./static/img/album',album_fname))
                album_path=os.path.join('./static/img/album',album_fname)
            else:
                return render_template('music_upload.html',data={'error':'Incorrect format of image file uploaded'})
        session_new_music=db.session
        new_song=Music(song_name=song_name,song_path=song_path)
        new_alb=Album(album_name=album_name,album_cover_image_path=album_path,music=new_song)
        new_art=Artist(artist_name=artist_name,artist_image_path=artist_path,music=new_song)
        try:
            session_new_music.add(new_song)
            session_new_music.commit()
            session_new_music.add(new_alb)
            session_new_music.commit()
            session_new_music.add(new_art)
            session_new_music.commit()
        except Exception as e:
            session_new_music.rollback()
            session_new_music.flush()
            return render_template('music_upload.html',data={'error':str(e)})
    return render_template('music_upload.html',data={'error':'None'})
#-----------------------------------------------------------------------------------------------
#class to wrap music objects
#-----------------------------------------------------------------------------------------------
class music_wrapper:
    def __init__(self,music_data):
        self.song_name=music_data.song_name
        self.song_path=music_data.song_path
        self.song_id=music_data.song_id
        self.artist_name=music_data.artist.artist_name
        self.album_name=music_data.album.album_name 
        self.artist_image_path=music_data.artist.artist_image_path
        self.album_image_path=music_data.album.album_cover_image_path

#-----------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------
@app.route('/play_music/')
def all_music():
    all_music_data=Music.query.all()
    music_list=[]
    for song in all_music_data:
        music_list.append(music_wrapper(song))
    return render_template('player.html',data=music_list)

#Running The Server
#-----------------------------------------------------------------------------------------------
if __name__=='__main__':
    db.create_all()
    app.run(port=8081,debug=True)
#-----------------------------------------------------------------------------------------------