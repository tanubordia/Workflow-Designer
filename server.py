from flask import Flask, render_template,request,g,flash,redirect,url_for,jsonify,json,session
from datetime import datetime,timedelta
import sqlite3


#initialising app
app = Flask(__name__)
app.secret_key = 'some_secret'


@app.route('/')
def index():
	#li = g.db.execute("SELECT * from Bookings,Rooms where Bookings.r_id = Rooms.r_id and b_date>=date('now') order by b_date asc;").fetchall();
	return render_template('index.html',data=li)

#connecting to DB before every request
@app.before_request
def before_request():
    g.db = sqlite3.connect('usersDB.db')

#closing connection after every request
@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()


@app.route('/signup', methods=['GET', 'POST'])
def test():
	if(request.method=='POST'):
		uid = request.form['sp_uid']
		passw = request.form['sp_pass']
		name = request.form['uname']
		email = request.form['email']
		phone = request.form['cell']
		city = request.form['city']

		if(len(uid)==0 or len(passw)==0 or len(name)==0 or len(email)==0 or len(phone)==0 or city=='City'):
			return jsonify(result = 'Please fill up all the fields')
		else:
			li = g.db.execute("SELECT * from Users WHERE uid = ?;",[uid]).fetchall();

			if(len(li)>0):
				return jsonify(result='User-id already exists! Please choose a different User-id.')
			else:
				g.db.execute("INSERT INTO Users VALUES (?,?,?,?,?,?);", (uid,passw,name,email,phone,city))
				g.db.commit()
				return jsonify(result='Signup successful! Now login with your new User-id.')


#clicking on Login
@app.route('/login',methods=['GET', 'POST'])
def login():
	if(request.method=='POST'):
		uid = request.form['uid']
		passw = request.form['pass']

		li = g.db.execute("SELECT pass from Users WHERE uid = ?;",[uid]).fetchall();
		nm = g.db.execute("SELECT uname from Users WHERE uid = ?;",[uid]).fetchall();

		if(len(li)==0):
			flash("Invalid User-id")
			return redirect(url_for('index'))

		else:
			if(str(passw)==str(li[0][0])):
				session['uname'] = str(nm[0][0])
				return render_template('choice.html',data = str(nm[0][0]))
			else:
				flash("Incorrect password")
				return redirect(url_for('index'))

if __name__ == '__main__':
  app.run(host= '0.0.0.0', port=5000, debug=True)
#host= '0.0.0.0', port=5000,
