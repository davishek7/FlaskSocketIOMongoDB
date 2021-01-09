from flask import Flask,render_template,request,redirect,url_for
from flask_socketio import SocketIO,join_room
from flask_login import LoginManager,login_user,logout_user,login_required,current_user
from db import get_user,save_user
from user import User

app=Flask(__name__)
socketio=SocketIO(app)
login_manager=LoginManager(app)

app.config['SECRET_KEY']='8d4c490be52bb2a9e83f20a76630727e'

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/register',methods=['GET','POST'])
def register():

	if current_user.is_authenticated:
		return redirect(url_for('index'))

	if request.method=='POST':
		username=request.form.get('username')
		email=request.form.get('email')
		password=request.form.get('password')

		save_user(username,email,password)
		return redirect(url_for('login'))

	return render_template('register.html')


@app.route('/login',methods=['POST','GET'])
def login():

	if current_user.is_authenticated:
		return redirect(url_for('index'))

	message=''

	if request.method=='POST':
		username=request.form.get('username')
		password_input=request.form.get('password')

		user=get_user(username)

		if user and user.check_password(password_input):
			login_user(user)
			return redirect(url_for('index'))
		else:
			message='Failed to login!'
	return render_template('login.html',message=message)

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('login'))

@app.route('/chat')
def chat():
	username=request.args.get('username')
	room=request.args.get('room')

	if username and room:
		return render_template('chat.html',username=username,room=room)
	else:
		return redirect(url_for('index'))

@socketio.on('send_message')
def handle_send_message_event(data):
	app.logger.info(f"{data['username']} has sent message to the room {data['room']}:{data['message']}")
	socketio.emit('receive_message',data,room=data['room'])

@socketio.on('join_room')
def handle_join_room_event(data):
	app.logger.info(f"{data['username']} has joined the room {data['room']}")
	join_room(data['room'])
	socketio.emit('join_room_announcement',data)

@login_manager.user_loader
def load_user(username):
	return get_user(username)

if __name__ == '__main__':
	socketio.run(app,debug=True)