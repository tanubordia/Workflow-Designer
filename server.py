from flask import Flask, render_template, request,g , flash,redirect, url_for,jsonify, json, session
from datetime import datetime,timedelta
import sqlite3


#initialising app
app = Flask(__name__)
app.secret_key = 'some_secret'

logged_user = dict()

def getPendingTasks():
	query = "select workflow_instance_id, current_stage_id from StageInstance where stage_actor = " + str(logged_user['id'])
	all_wfs = g.db.execute(query).fetchall()
	data_list=[]
	for wf in all_wfs:
		stage_id = wf[1]
		workflow_instance_id = wf[0]
		query = "select name, id from Action where stage_id = " + str(stage_id)
		all_actions = g.db.execute(query).fetchall()
		query = "select workflow_id from WorkflowInstance where id = " + str(workflow_instance_id)
		wf_id = g.db.execute(query).fetchall()[0][0]
		query = "select name from Workflow where id = " + str(wf_id)
		wf_name = g.db.execute(query).fetchall()[0][0]
		query = "select name,numberofactions from stage where id = " + str(stage_id)
		stage_name = g.db.execute(query).fetchall()
		for action in all_actions:
			data_list1=[]
			data_list1.append(workflow_instance_id)
			data_list1.append(stage_name[0][0])
			# data_list1.append(stage_name[0][1])
			data_list1.append(wf_name)
			# data_list1.append([])
			data_list1.append([action[0], action[1]])
			data_list.append(data_list1)
	return data_list


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
			name = "select username from usermaster where id="+str(id[0][0])
			username=g.db.execute(name).fetchall();
			logged_user['name'] = username[0][0]
			logged_user['role'] = role[0][0]
			logged_user['id'] = id[0][0]
			if(role[0][0]=="Admin"):
				u_id=int(id[0][0])
				findwf="Select * from workflow where admin_id="+str(u_id)
				wfs=g.db.execute(findwf).fetchall()
				return render_template('adminpage.html', u_id=u_id,data=wfs, role =role[0][0], name = username[0][0])
			else:
				return render_template('userlogin.html', u_id=id[0][0],role= role[0][0],name = username[0][0])

@app.route('/startworkflow', methods=['GET'])
def startworkflow():
	findwf="Select * from workflow"
	wfs=g.db.execute(findwf).fetchall();
	return render_template('userdashboard.html',u_id=logged_user['id'],role= logged_user['role'], data=wfs,name = logged_user['name'])

@app.route('/viewtasks', methods=['GET', 'POST'])
def viewtasks():
	if(request.method == 'GET'):
		data_list=getPendingTasks()
		return render_template('viewtasks.html', u_id=logged_user['id'],role= logged_user['role'], data=data_list,name = logged_user['name'])
	else:
		temp = request.form['doaction'].split(",")
		workflow_instance_id = temp[0]
		action_id = temp[1]
		query = "select current_stage_id from StageInstance where workflow_instance_id = " + str(workflow_instance_id)
		current_stage_id = g.db.execute(query).fetchall()[0][0]
		query = "select next_stage from StageTransition where prev_stage = " + str(current_stage_id) + " and action = " + str(action_id)
		next_stage_id = g.db.execute(query).fetchall()[0][0]
		query = "select numberofactions from Stage where id = " + str(next_stage_id)
		num_actions = g.db.execute(query).fetchall()[0][0]
		if(num_actions > 0):
			query = "select user_id from StageActorInstance where workflow_instance_id = " + str(workflow_instance_id) + " and stage_id = " + str(next_stage_id)
			stage_actor = g.db.execute(query).fetchall()[0][0]
			query = "update StageInstance set current_stage_id = " + str(next_stage_id) + " , stage_actor = " + str(stage_actor) + " where workflow_instance_id = " + str(workflow_instance_id)
			g.db.execute(query).fetchall()
			g.db.commit()
		else:
			query = "delete from WorkflowInstance where id = " + str(workflow_instance_id)
			g.db.execute(query).fetchall()
			g.db.commit()
			query = "delete from StageInstance where workflow_instance_id = " + str(workflow_instance_id)
			g.db.execute(query).fetchall()
			g.db.commit()
		data_list=getPendingTasks()
		return render_template('viewtasks.html', u_id=logged_user['id'],role= logged_user['role'], data=data_list,name = logged_user['name'])

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

			return render_template('designStages.html', u_id=u_id, wf_id=wfid, wfname = wfname, stagenumber = int(1), num_stage=number)
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
			# NumStages = int(NumStages[0][0])
			actionNumber = 0
			if int(actionNumber) < int(numActions):
				return render_template('designActions.html', u_id=u_id, wf_id=wf_id, wfname = wfname, stage_id = stage_id, stagename = stagename, stagenumber = int(stagenumber), actionNumber = int(actionNumber + 1), num_stage=NumStages)
			elif int(stagenumber) < int(NumStages) :
				return render_template('designStages.html', u_id = u_id, wf_id = wf_id, wfname = wfname, stagenumber = int(stagenumber) + 1,num_stage=NumStages)
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
					return render_template('designStages.html', u_id = u_id, wf_id = wf_id, wfname = wfname, stagenumber = int(stagenumber) + 1, num_stage=NumStages)
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
		sql1 = "select role,username from usermaster where id="+str(u_id)
		rolename=g.db.execute(sql1).fetchall();
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
				# data= []
				# for wf in wfs:
				# 	data.append("WorkFlow ID: " + str(wf[0]) + " |  Workflow Name: " + str(wf[1]))
				return render_template('adminpage.html', u_id=u_id,data=wfs, role = rolename[0][0], name = rolename[0][1])
			action_id = int(actionList[actionNumber - 1][0])
			actionName = str(actionList[actionNumber - 1][2])
			stagename = str(stagesList[stagenumber - 1][2])
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
	stages="Select id,name from stage where workflow_id="+str(wf_id)
	stagelist=g.db.execute(stages).fetchall();
	actionandstage=[]
	for stage in stagelist:
		actionstr="Select name from Action where stage_id="+str(stage[0])
		actions=g.db.execute(actionstr).fetchall();
		print(actions)
		action_list=[]
		for action in actions:
			action_list.append(action[0].encode("utf-8"))
		actionandstage.append([stage,action_list])
	print(actionandstage)
	return render_template('viewworkflow.html',workflow=l[0],data=actionandstage,wf_id=wf_id)


@app.route('/instancewf', methods=['GET', 'POST'])
def instancewf():
	if request.method == 'POST':

		wf_id=request.form['wf_id']
		print(wf_id)
		snum = "select numofstages from Workflow where id="+str(wf_id)
		stage_n = g.db.execute(snum).fetchall();
		sql="""INSERT INTO WorkflowInstance(workflow_id) VALUES ({});""".format(wf_id)
		g.db.execute(sql)
		g.db.commit()
		stages="Select id,name from stage where name<>'End Workflow' and workflow_id="+str(wf_id)
		stagelist=g.db.execute(stages).fetchall();
		users = "select id,role,username from usermaster where role='User'"
		user_info = g.db.execute(users).fetchall();
		stage_data = []
		c=1
		for i in stagelist:
			data =[]
			data.append(c);
			data.append(i[0])
			data.append(i[1])
			stage_data.append(data)
			c=c+1
		print(stage_data)
		return render_template('instancewf.html', stage_num = stage_n[0][0], stagelist = stage_data, users = user_info)


	return render_template('instancewf.html',stage_num = stage_n[0][0], stagelist = stage_data, users = user_info)

@app.route('/workflowstruct', methods=['GET', 'POST'])
def workflowstruct():
	if request.method == 'POST':

		sql = "select * from workflowinstance ORDER BY id DESC LIMIT 1";
		wf_id = g.db.execute(sql).fetchall();
		wf = "select id, name, numofstages from workflow where id="+str(wf_id[0][1])
		work_f = g.db.execute(wf).fetchall();
		# print(work_f)
		snum = "select numofstages from Workflow where id="+str(wf_id[0][1])
		stage_n = g.db.execute(snum).fetchall();
		stage_actor={}
		for i in range(1,stage_n[0][0]+1):
			stage_actor[i] = request.form['stage_actor'+str(i)]
		# print(stage_actor)
		stages="Select id,name from stage where name<>'End Workflow' and workflow_id="+str(wf_id[0][1])
		stagelist=g.db.execute(stages).fetchall();
		# print(stagelist)
		for i in range(1,stage_n[0][0]+1):
			g.db.execute("INSERT INTO StageActorInstance(stage_id, user_id, workflow_instance_id) VALUES (?, ?, ?)", (stagelist[i-1][0], stage_actor[i], wf_id[0][0])).fetchall()
			g.db.commit()

		query = "select id from Stage where workflow_id = " + str(wf_id[0][1]) + " order by id limit 1"
		start_stage_id = g.db.execute(query).fetchall()[0][0]

		query = "select user_id from StageActorInstance where workflow_instance_id = " + str(wf_id[0][0]) + " and stage_id = " + str(start_stage_id)
		start_stage_actor = g.db.execute(query).fetchall()[0][0]

		g.db.execute("insert into StageInstance(workflow_instance_id, current_stage_id, stage_actor) values (?, ?, ?)", (wf_id[0][0], start_stage_id, start_stage_actor)).fetchall()
		g.db.commit()

		data =[]
		for i in range(1,stage_n[0][0]+1):
			data1=[]
			data1.append(stagelist[i-1][0])
			data1.append(stagelist[i-1][1])
			actions = "select numberofactions from stage where id="+str(stagelist[i-1][0])
			num_actions = g.db.execute(actions).fetchall();
			data1.append(num_actions[0][0])
			data1.append(stage_actor[i])
			name = "select username from usermaster where id="+str(stage_actor[i])
			actor_name = g.db.execute(name).fetchall();
			data1.append(actor_name[0][0])
			data.append(data1)

		print(data)


		return render_template('workflowstruct.html', wf = work_f, data = data)

	return render_template('workflowstruct.html',wf = work_f, data = data)



if __name__ == '__main__':
  app.run(host= '0.0.0.0', port=5000, debug=True)
#host= '0.0.0.0', port=5000,
