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
				findwf="Select * from workflow"
				wfs=g.db.execute(findwf).fetchall();
				print(1)
				return render_template('userdashboard.html',u_id=id[0][0], data=wfs)

#clicking on design
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
			wfid = g.db.execute("SELECT last_insert_rowid();").fetchall()
			wfid = int(wfid[0][0])

			return render_template('designStages.html', u_id=u_id, wf_id=wfid, wfname = wfname, stagenumber = int(1))
	return ""

@app.route('/stagedesign', methods=['GET', 'POST'])
def stagedesign():
	if(request.method=='POST'):
		u_id=request.form['u_id']
		wf_id=request.form['wf_id']
		wfname = request.form['wfname']
		stagenumber = request.form['stagenumber']
		stagename = request.form['stagename']
		actionname = request.form['actionname']
		if(len(stagename) == 0 or len(wfname) == 0):
			return jsonify(result = 'Please fill up all the fields')
		else:
			g.db.execute("INSERT INTO Stage(workflow_id, name) VALUES (?,?);",(wf_id, stagename) )
			g.db.commit()
			stageId = g.db.execute("SELECT last_insert_rowid();").fetchall()
			stageId = int(stageId[0][0])
			g.db.execute("INSERT INTO Action(stage_id, name) VALUES (?,?);", (stageId, actionname))
			g.db.commit()
			NumStages = g.db.execute("SELECT numofstages FROM Workflow WHERE id = ?", (wf_id, )).fetchall()
			NumStages = int(NumStages[0][0])
			if int(stagenumber) < int(NumStages) :
				return render_template('designStages.html', u_id=u_id, wf_id=wf_id, wfname = wfname, stagenumber = int(stagenumber) + 1)
			else :
				return ""





#clicking on
@app.route('/viewworkflow', methods=['GET', 'POST'])
def viewworkflow():

	print(1);
	wf_id=request.form['wf_id']
	print(wf_id)
	wfid="Select * from workflow where id="+str(wf_id)
	l=g.db.execute(wfid).fetchall();
	print(l)
	stages="Select id,name from stage where workflow_id="+str(wf_id)
	stagelist=g.db.execute(stages).fetchall();
	actionandstage=[]
	for stage in stagelist:
		print(stage)
		actionstr="Select name from Action where stage_id="+str(stage[0])
		actions=g.db.execute(actionstr).fetchall();
		print(actions)


		actionandstage.append([stage,actions])
	print(actionandstage)
	return render_template('viewworkflow.html',workflow=l[0],data=actionandstage,wf_id=wf_id)


@app.route('/instancewf', methods=['GET', 'POST'])
def instancewf():
	 if request.method == 'POST':
		print("wassup")
		wf_id=request.form['wf_id']
		print(wf_id)


		sql="""INSERT INTO WorkflowInstance(workflow_id) VALUES ({});""".format(wf_id)
		g.db.execute(sql)
		g.db.commit()

		return "hi"
	 return ""




if __name__ == '__main__':
  app.run(host= '0.0.0.0', port=5000, debug=True)
#host= '0.0.0.0', port=5000,
