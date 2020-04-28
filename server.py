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
		findid = "SELECT id from usermaster WHERE username=\""+ name +"\" and password=\""+passw+"\""

		role= g.db.execute(findrole).fetchall();
		id= g.db.execute(findid).fetchall();



		if(len(role)==0):
			flash("Invalid User-id or Password")
			return redirect(url_for('index'))

		else:
			if(role[0][0]=="Admin"):
				u_id=int(id[0][0])
				findwf="Select * from workflow where admin_id="+str(u_id)
				wfs=g.db.execute(findwf).fetchall();
				data= []
				for wf in wfs:
					data.append("WorkFlow ID: " + str(wf[0]) + " |  Workflow Name: " +wf[1].encode("utf-8"))

				return render_template('adminpage.html', u_id=u_id,data=data)
			else:
				return name


@app.route('/design', methods=['GET', 'POST'])
def design():
	if(request.method=='POST'):
		u_id=request.form['u_id']
		wfname = request.form['wfname']
		cust_notif = request.form['cust_notif']

		number = request.form['numberofstages']


		if(len(wfname)==0 or len(cust_notif)==0 or number==0):
			return jsonify(result = 'Please fill up all the fields')
		else:
			g.db.execute("INSERT INTO Workflow(name,customNotification,numofstages,admin_id) VALUES (?,?,?,?);",(wfname,cust_notif,number,u_id) )

			g.db.commit()
			wfid = g.db.execute("SELECT last_insert_rowid();")
	
				
			return render_template('designStages.html', wfid=wfid)
	return ""





if __name__ == '__main__':
  app.run(host= '0.0.0.0', port=5000, debug=True)
#host= '0.0.0.0', port=5000,
