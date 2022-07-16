from time import localtime, strftime
from flask import Flask, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user,LoginManager,login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import InputRequired,length, ValidationError
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO, send, emit, join_room, leave_room

#configuring app
app=Flask(__name__)
db=SQLAlchemy(app)
bcrypt=Bcrypt(app)
#configuring database
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///AdminUsers.db'

app.config['SECRET_KEY']='thisisasecretkey'

#initializing flask-socketio
socketio = SocketIO(app, cors_allowed_origins="*")
GROUPS=['grpOne','grpTwo','grpThree','grpFour']

#configurring login
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view="login"

@login_manager.user_loader
def loadUser(id):
    return AdminUsers.query.get(int(id))

# creating users table
class AdminUsers(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    FirstName=db.Column(db.String(80),nullable=False)
    LastName = db.Column(db.String(80), nullable=False)
    UserId = db.Column(db.String(200), nullable=False)
    Password=db.Column(db.String(95),nullable=False)
    
class RegistrationForm(FlaskForm):
    def __init__(self,userId):
        self.userId=userId
    def validate_username(self,userId):
        existingMailId=Users.query.filter_by(
            user=userId.data).first()
        if existingMailId:
            raise ValidationError(
                "This mail Id is allready exists! please try login or register with different mail"
            )

#routing to login when user is not logged in
@app.route('/',methods=['GET','POST'])
def home():
    if request.method == 'POST':
        name=request.form.get('user')
        password=request.form.get('passwd')
        user=AdminUsers.query.filter_by(UserId=name).first()
        loadUser(user.id)
        if user:
            if bcrypt.check_password_hash(user.Password,password):
                login_user(user)
                return redirect(url_for('chat'))
    return render_template('login.html')


#to logout
@app.route('/logout',methods=['POST','GET'])
@login_required
def logout():
    logout_user()
    return redirect('/')

#to register
@app.route('/register',methods=['POST','GET'])
def register():
    if request.method=='POST':
        Firstname=request.form.get('firstname')
        Lastname=request.form.get('lastname')
        userid = request.form.get('user')
        password=request.form.get('password')
        form = RegistrationForm(userid)
        hashedPaswd=bcrypt.generate_password_hash(password)
        newUser=AdminUsers(FirstName=Firstname,LastName=Lastname,UserId=userid,Password=hashedPaswd)
        db.session.add(newUser)
        db.session.commit()
        return redirect('/')
    return render_template('Register.html')

#loggedin page for user
@app.route('/chat',methods=['POST','GET'])
@login_required
def chat():
    return render_template('chat.html',username=current_user.UserId, groups=GROUPS)

# creating message event handler
@socketio.on('message')
def message(data):
    print(f"\n\n{data}\n\n")
    send({'msg': data['msg'], 'username': data['username']},group=data['group'])

@socketio.on('join')
def join(data):
    join_room(data['group'])
    send({'msg':data['username']+"has joined the "+data['group']+" group"},room=data['group'])

@socketio.on('leave')
def leave():
    leave_room(data['group'])
    send({'msg': data['username'] + "has left the " + data['group'] + " group"}, room=data['group'])
    

if __name__=='__main__':
    socketio.run(app, debug=False)