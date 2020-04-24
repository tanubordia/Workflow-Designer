from flask import Flask, render_template,request,g,flash,redirect,url_for,jsonify,json,session
from datetime import datetime,timedelta
import sqlite3


#initialising app
app = Flask(__name__)
app.secret_key = 'some_secret'


@app.route('/')
def index():

	return render_template('index.html')

#connecting to DB before every request
@app.before_request
def before_request():
    g.db = sqlite3.connect('wf.db')

#closing connection after every request
@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()


@app.route('/signup', methods=['GET', 'POST'])
def test():
	if(request.method=='POST'):
		name = request.form['uname']
		passw = request.form['sp_pass']

		role = request.form['role']


		if(len(name)==0 or len(passw)==0 or role=='Role'):
			return jsonify(result = 'Please fill up all the fields')
		else:
			g.db.execute("INSERT INTO UserMaster(username,password,role) VALUES (?,?,?);",(name,passw,role) )
			g.db.commit()
			return jsonify(result='Signup successful! Now login with your new User-id.')


#clicking on Login
@app.route('/login',methods=['GET', 'POST'])
def login():
	if(request.method=='POST'):
		name = request.form['u_name']
		passw = request.form['pass']


		findrole = "SELECT role from usermaster WHERE username=\""+ name +"\" and password=\""+passw+"\""
		print(findrole)
		role= g.db.execute(findrole).fetchall();



		if(len(role)==0):
			flash("Invalid User-id or Password")
			return redirect(url_for('index'))

		else:
			if(role[0][0]=="Admin"):

				return render_template('adminpage.html')
			else:
				return name


if __name__ == '__main__':
  app.run(host= '0.0.0.0', port=5000, debug=True)
#host= '0.0.0.0', port=5000,
