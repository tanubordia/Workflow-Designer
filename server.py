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
					data.append("WorkFlow ID: " + str(wf[0]) + " |  Workflow Name: " + str(wf[1]))

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
		numActions = request.form['numActions']
		if(len(stagename) == 0 or len(wfname) == 0):
			return jsonify(result = 'Please fill up all the fields')
		else:
			g.db.execute("INSERT INTO Stage(workflow_id, name, numberofactions) VALUES (?,?,?);",(wf_id, stagename, numActions) )
			g.db.commit()
			stage_id = g.db.execute("SELECT last_insert_rowid();").fetchall()
			stage_id = int(stage_id[0][0])
			NumStages = g.db.execute("SELECT numofstages FROM Workflow WHERE id = ?", (wf_id, )).fetchall()
			NumStages = int(NumStages[0][0])
			actionNumber = 0
			if int(actionNumber) < int(numActions):
				return render_template('designActions.html', u_id=u_id, wf_id=wf_id, wfname = wfname, stage_id = stage_id, stagename = stagename, stagenumber = int(stagenumber), actionNumber = int(actionNumber + 1))
			elif int(stagenumber) < int(NumStages) :
				return render_template('designStages.html', u_id = u_id, wf_id = wf_id, wfname = wfname, stagenumber = int(stagenumber) + 1)
			else :
				return ""

@app.route('/actiondesign', methods=['GET', 'POST'])
def actiondesign():
	if(request.method == 'POST'):
		u_id=request.form['u_id']
		wf_id=request.form['wf_id']
		wfname = request.form['wfname']
		stage_id = request.form['stage_id']
		stagenumber = request.form['stagenumber']
		stagename = request.form['stagename']
		actionNumber = request.form['actionNumber']
		actionName = request.form['actionName']
		if(len(actionName) == 0):
			return jsonify(result = 'Please fill up all the fields')
		else:
			stage_id = int(stage_id)
			g.db.execute("INSERT INTO Action(stage_id, name) VALUES (?,?);", (stage_id, actionName))
			g.db.commit()
			numActions = g.db.execute("SELECT numberofactions FROM Stage WHERE id = ?", (stage_id, )).fetchall()
			numActions = int(numActions[0][0])
			if int(actionNumber) < int(numActions):
				return render_template('designActions.html', u_id=u_id, wf_id=wf_id, wfname = wfname, stage_id = stage_id, stagename = stagename, stagenumber = int(stagenumber), actionNumber = int(actionNumber) + 1)
			else :
				NumStages = g.db.execute("SELECT numofstages FROM Workflow WHERE id = ?", (wf_id, )).fetchall()
				NumStages = int(NumStages[0][0])
				if int(stagenumber) < int(NumStages) :
					return render_template('designStages.html', u_id = u_id, wf_id = wf_id, wfname = wfname, stagenumber = int(stagenumber) + 1)
				else:
					finalStageName = "End Workflow"
					numActions = 0
					wf_id = int(wf_id)
					g.db.execute("INSERT INTO Stage(workflow_id, name, numberofactions) VALUES (?,?,?);",(wf_id, finalStageName, numActions))
					g.db.commit()
					actionNumber = 0
					stagenumber = 0
					stagenumber = int(stagenumber) + 1
					stagesList = g.db.execute("SELECT * FROM Stage WHERE workflow_id = ? ORDER BY id", (wf_id, )).fetchall()
					stage_id = int(stagesList[stagenumber - 1][0])
					actionNumber = int(actionNumber) + 1
					actionList = g.db.execute("SELECT * FROM Action WHERE stage_id = ? ORDER BY id", (stage_id, )).fetchall()
					action_id = int(actionList[actionNumber - 1][0])
					actionName = actionList[actionNumber - 1][2]
					stagename = stagesList[stagenumber - 1][2]
					print(actionName, stagename)
					return render_template('stageTransition.html', u_id = u_id, wf_id = wf_id, wfname = wfname, stage_id = stage_id, stagenumber = stagenumber, stagename = stagename, action_id = action_id, actionNumber = actionNumber, actionName = actionName, data = stagesList)


@app.route('/stageTransition', methods=['GET', 'POST'])
def stageTransition():
	if(request.method == 'POST'):
		u_id = request.form['u_id']
		wf_id = request.form['wf_id']
		wfname = request.form['wfname']
		stage_id = request.form['stage_id']
		stagenumber = request.form['stagenumber']
		stagename = request.form['stagename']
		action_id = request.form['action_id']
		actionNumber = request.form['actionNumber']
		actionName = request.form['actionName']
		transitionStateId = request.form['transitionStateId']
		transitionStateId = int(transitionStateId)
		g.db.execute("INSERT INTO StageTransition(prev_stage, action, next_stage) VALUES (?, ?, ?)", (stage_id, action_id, transitionStateId)).fetchall()
		g.db.commit()
		numActions = g.db.execute("SELECT numberofactions FROM Stage WHERE id = ?", (stage_id, )).fetchall()
		numActions = int(numActions[0][0])
		NumStages = g.db.execute("SELECT numofstages FROM Workflow WHERE id = ?", (wf_id, )).fetchall()
		NumStages = int(NumStages[0][0])
		print(transitionStateId, numActions, NumStages, actionNumber, stagenumber)
		if(int(numActions) == int(actionNumber)):
			actionNumber = 0
			stagenumber = int(stagenumber) + 1
			stagesList = g.db.execute("SELECT * FROM Stage WHERE workflow_id = ? ORDER BY id", (wf_id, )).fetchall()
			stage_id = int(stagesList[stagenumber - 1][0])
			actionNumber = int(actionNumber) + 1
			actionList = g.db.execute("SELECT * FROM Action WHERE stage_id = ? ORDER BY id", (stage_id, )).fetchall()
			if(len(actionList) == 0):
				findwf="Select * from workflow where admin_id="+str(u_id)
				wfs=g.db.execute(findwf).fetchall();
				data= []
				for wf in wfs:
					data.append("WorkFlow ID: " + str(wf[0]) + " |  Workflow Name: " + str(wf[1]))
				return render_template('adminpage.html', u_id=u_id,data=data)
			action_id = int(actionList[actionNumber - 1][0])
			actionName = str(actionList[actionNumber - 1][2])
			return render_template('stageTransition.html', u_id = u_id, wf_id = wf_id, wfname = wfname, stage_id = stage_id, stagenumber = stagenumber, stagename = stagename, action_id = action_id, actionNumber = actionNumber, actionName = actionName, data = stagesList)
		else:
			stagesList = g.db.execute("SELECT * FROM Stage WHERE workflow_id = ? ORDER BY id", (wf_id, )).fetchall()
			actionNumber = int(actionNumber) + 1
			actionList = g.db.execute("SELECT * FROM Action WHERE stage_id = ? ORDER BY id", (stage_id, )).fetchall()
			actionName = str(actionList[actionNumber - 1][2])
			action_id = int(actionList[actionNumber - 1][0])
			return render_template('stageTransition.html', u_id = u_id, wf_id = wf_id, wfname = wfname, stage_id = stage_id, stagenumber = stagenumber, stagename = stagename, action_id = action_id, actionNumber = actionNumber, actionName = actionName, data = stagesList)

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
		print(actions)
	print(actionandstage)
	return render_template('viewworkflow.html',workflow=l[0],data=actionandstage,wf_id=wf_id)


@app.route('/instancewf', methods=['GET', 'POST'])
def instancewf():
	if request.method == 'POST':
		
		wf_id=request.form['wf_id']
		print(wf_id)


		sql="""INSERT INTO WorkflowInstance(workflow_id) VALUES ({});""".format(wf_id)
		g.db.execute(sql)
		g.db.commit()

		
	return ""




if __name__ == '__main__':
  app.run(host= '0.0.0.0', port=5000, debug=True)
#host= '0.0.0.0', port=5000,
