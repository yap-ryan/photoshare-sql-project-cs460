######################################
# author ben lawson <balawson@bu.edu>
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################


#testing 

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login

#for image uploading
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Bec00YuDio!!'
app.config['MYSQL_DATABASE_DB'] = 'photoshareTEST3'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from User")
users = cursor.fetchall()

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from User")
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM User WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd
	return user

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   	<form action='login' method='POST'>
					<input type='text' name='email' id='email' placeholder='email'></input>
					<input type='password' name='password' id='password' placeholder='password'></input>
					<input type='submit' name='submit'></input>
			   	</form></br>
		   		<a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM User WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out')

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html')

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
	return render_template('register.html', supress='True')

@app.route("/register", methods=['POST'])
def register_user():
	try:
		email=request.form.get('email')
		password=request.form.get('password')
	except:
		print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	if test:
		print(cursor.execute("INSERT INTO User (email, password) VALUES ('{0}', '{1}')".format(email, password)))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('hello.html', name=email, message='Account Created!')
	else:
		print("couldn't find all tokens")
		return flask.redirect(flask.url_for('register'))

def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT data, photo_id, caption FROM Photo WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE return a list of tuples, [(imgdata, pid, caption), ...]

def getAlbumsPhotos(albumid):
	cursor = conn.cursor()
	cursor.execute("SELECT data FROM Photo WHERE album_id = '{0}'".format(albumid))
	return cursor.fetchall() #NOTE return a list of tuples, [(imgdata, pid, caption), ...]


def getUsersAlbums(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT album_name FROM Album WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall()  #return list of all of the albums owned by that user 


def getAllUserIds():
	cursor = conn.cursor()
	cursor.execute("SELECT user_id FROM User")
	return cursor.fetchall()  #return list of all of the user ids 


def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id FROM User WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def getAlbumIdFromName(name):
	cursor = conn.cursor()
	cursor.execute("SELECT album_id FROM ALbum WHERE album_name = '{0}'".format(name))
	return cursor.fetchone()[0]


def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM User WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
#end login code

@app.route('/profile')
@flask_login.login_required
def protected():
	return render_template('hello.html', name=flask_login.current_user.id, message="Here's your profile")

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():


	uid = getUserIdFromEmail(flask_login.current_user.id)
	album_list = getUsersAlbums(uid)

	if request.method == 'POST':
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		photo_data =imgfile.read()
		cursor = conn.cursor()
		albumname = request.form.get('selectalbum')
		likes = 0

		album_id = getAlbumIdFromName(albumname)		
		cursor.execute('''INSERT INTO Photo (data, caption, album_id, user_id, likes) VALUES (%s, %s ,%s,%s, %s)''', (photo_data, caption, album_id, uid, likes))
		conn.commit()
		return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(uid), base64=base64)
	
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		return render_template('upload.html', album_list = album_list)
#end photo uploading code




#begin create new album code 

ALLOWED_EXTENSIONS2 = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS2

@app.route('/createalbum', methods=['GET', 'POST'])
@flask_login.login_required
def create_new_album():


	uid = getUserIdFromEmail(flask_login.current_user.id)

	if request.method == 'POST':
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		photo_data =imgfile.read()
		cursor2 = conn.cursor()
		createdalbum = request.form.get('albumname')
		date = request.form.get('date')
		likes = 0

		cursor2.execute('''INSERT INTO Album (album_name, creation_date, user_id) VALUES (%s, %s, %s )''', (createdalbum, date, uid))
		album_id = getAlbumIdFromName(createdalbum)		
		cursor2.execute('''INSERT INTO Photo (data, caption, album_id, user_id, likes) VALUES (%s, %s ,%s,%s, %s)''', (photo_data, caption, album_id, uid, likes))
		conn.commit()
		return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(uid), base64=base64)
	
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		return render_template('createalbum.html')

#end create new album code 



#begin view all albums code 

@app.route('/viewallalbums', methods=['GET', 'POST'])
def viewAllAlbums(): 
	user_id_list = getAllUserIds()
	album_list_of_all_users = []

	for x in user_id_list :

		album_one_user = getUsersAlbums(x[0])
		
		for y in album_one_user : 
			album_list_of_all_users.append(y)


	return render_template('viewallalbums.html', album_list = album_list_of_all_users, user_list = user_id_list)


#end view all albums code 



# begin view one album for unregistered user code 

@app.route('/viewonealbumunreg', methods=['GET', 'POST'])
def viewonealbumunreg(): 

	args = request.args 

	album_name = args.get('album_name')
	
	album_id = getAlbumIdFromName(album_name)

	photos = getAlbumsPhotos(album_id)
	return render_template('viewonealbumunreg.html',  photos=photos, base64=base64)

# end view one album for unregistered user code 




#begin view user albums code 

@app.route('/viewuseralbums', methods=['GET', 'POST'])
@flask_login.login_required
def viewUserAlbums(): 
	uid = getUserIdFromEmail(flask_login.current_user.id)
	albums = getUsersAlbums(uid)

	return render_template('viewuseralbums.html', album_list = albums)


#begin view user albums code 



# begin view one album for registered user code 

@app.route('/viewonealbumuser', methods=['GET', 'POST'])
def viewonealbumuser(): 

	args = request.args 

	album_name = args.get('album_name')
	
	album_id = getAlbumIdFromName(album_name)

	photos = getAlbumsPhotos(album_id)
	return render_template('viewonealbumunreg.html',  photos=photos, base64=base64)

# end view one album for registered user code 




#default page
@app.route("/", methods=['GET'])
def hello():
	return render_template('hello.html', message='Welcome to Photoshare')


if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)

