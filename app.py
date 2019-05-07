from flask import render_template,request, redirect, url_for,flash,session
from database import app, db, User, Discussion, Message
from utils import validate_password



app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# all the topics of discussion
@app.route('/')
def index():
  discussions = Discussion.query.all()
  return render_template('index.html', discussions=discussions,session=session)

# messages for each topic 
@app.route('/messages/<int:discussion_id>/', methods=['POST', 'GET'])
def messages(discussion_id):
	if request.method == 'POST':
		user = User.query.filter_by(username=session['username']).first()
		message = Message(
			text=request.form['text'], 
			discussion_id=discussion_id, 
			user_id=user.id)
		db.session.add(message)
		db.session.commit()    

	messages = Message.query.filter_by(discussion_id=discussion_id).order_by(Message.date.desc()).all()
	discussion = Discussion.query.filter_by(id=discussion_id).first()
	
	# .order_by(model.Entry.amount.desc())

	for message in messages:
		# print(message.user_id)
		message.user = User.query.filter_by(id=message.user_id).first()
		# print(user)   
	return render_template('messages.html',messages=messages, discussion=discussion)



# signup 
@app.route('/signup',methods = ['GET', 'POST'])
def signup():
	if 'username' in session:
		return redirect(url_for('index'))
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		if User.query.filter_by(username=username).first() == None:
			if password_check(password):
				user = User(username=username,password=password)
				flash('User saved succefuly')
				db.session.add(user)
				db.session.commit()
				session['username'] = username
				return redirect(url_for('index'))
			else:
				flash(' password is too weak')
		else:
			flash('Username already exist')
	return render_template('signup.html')

	


# login
@app.route('/signin', methods = ['GET', 'POST'])
def signin():
	if 'chances' not in session:
		session['chances'] = 3 
	print(session['chances'])
	if 'username' in session:
		return redirect(url_for('index'))

	if request.method == 'POST':
		if session['chances'] <= 1:
			flash('Too many login attempts')
		else:
			user = User.query.filter_by(
				username=request.form['username'],
				password=request.form['password']
			).first()
			if user:
				session['username'] = request.form['username']
				return redirect(url_for('index'))
			else:
				session['chances'] -= 1 
				flash('Invalid credentials you have {} chances remaining'.format(session['chances']))
	return render_template('signin.html')

# logout
@app.route('/logout')
def logout():
	session.pop('username')
	return redirect(url_for('index'))


@app.route('/profile/<int:user_id>/')
def profil(user_id):
	user = User.query.filter_by(id = user_id).first()
	messages = Message.query.filter_by(user_id = user_id).order_by(Message.date.desc()).all()
	return render_template('profile.html', user=user, messages=messages)


@app.route('/profile/<int:user_id>/password', methods=['POST'])
def password_update(user_id):
	user = User.query.filter_by(
		username=session['username'],
		password=old_password
	).first()

	if user:
		user.password = request.form['new-password']
		db.session.commit()
	else:
		flash('Invalid password')

	return redirect( url_for('profile', user_id=user_id) )

# hello word whatsup?

@app.route('/profile/<int:user_id>/username', methods=['POST'])
def username_update(user_id):
	new_username = request.form['new-username']
	if User.query.filter_by(id=user_id).first():
		lash('Username is already taken')
	else:
		user = User.query.filter_by(id=user_id).first()
		user.username = new_username
		db.session.commit()
		session['username'] = new_username
			

	return redirect( url_for('profile', user_id=user.id) )
					
