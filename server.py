from flask import render_template,Flask,request,session
import pymongo

client=pymongo.MongoClient('mongodb+srv://revanth:nagasai20032104@cluster0.tqwer.mongodb.net/test')
app=Flask(__name__)
app.secret_key='99009'

@app.route('/')
def home():
    return render_template('main_reg.html')

@app.route('/reg_verify',methods=['get'])
def reg_verify():
    name=request.args.get('name')
    phno=request.args.get('phno')
    email=request.args.get('email')
    aadhar=request.args.get('aadhar')
    psw=request.args.get('psw')
    doc=client['doctors']['Clients']
    data=doc.find()
    for i in data:
        if name == i['name']:
            return render_template('main_reg.html',res="existing user") 
    doc.insert_one({
        'name':name,
        'phno':phno,
        'email':email,
        'aadhar':aadhar,
        'psw':psw,
    })
    return render_template('login.html')

@app.route('/login')
def login():
    return render_template('login1.html')

@app.route('/login1')
def login1():
    return render_template('login2.html')

@app.route('/login_verify',methods=['post'])
def verify():
    name=request.form['uname']
    pas=request.form['psw']
    doc=client['doctors']['Clients']
    data=doc.find()
    for i in data:
        if i['name']==name and i['psw']==pas:
            session['u']=name
            session['w']='owner'
            return render_template('abc.html')
    return render_template('login1.html',res='invalid user or password')

@app.route('/main')
def main():
    if session['w']=='name':
        return render_template('appointments.html')
    return render_template('abc.html')

@app.route('/admin_verify',methods=['post'])
def admin_verify():
    name=request.form['uname']
    pas=request.form['psw']
    doc=client['doctors']['details']
    data=doc.find()
    for i in data:
        if i['name']==name and i['psw']==pas:
            session['u']=name
            session['w']='name'
            doc1=client['doctors']['appointments']
            data=doc1.find()
            data2=[]
            for i in data:
                i=dict(i)
                if i['owner']==session['u']:
                    data2.append(i)
            return render_template('appointments.html',data=data2,name='name')
    return render_template('login2.html',res='invalid user or password')


@app.route('/profile',methods=['GET'])
def profile():
    name=request.args.get('name')
    session['n']=name
    doc=client['doctors']['details']
    for i in doc.find():
        print(i)
        if i['name']==name:
            i=list(i.values())
            session['a']=i[5]
            return render_template('profile.html',i=i)

@app.route('/form')
def appoint():
    return render_template('form.html')

@app.route('/submit',methods=['post'])
def submit():
    owner=session['n']

    doc1=client['doctors']['appointments']
    appointment_data=doc1.find()
    
    data1=request.form
    date=request.form['date']
    time=request.form['time']
    asserts=request.form['asserts']
    data1=dict(data1)

    #check empty values
    for i in data1:
        if data1[i] == '':
            return render_template('form.html',res="**enter "+i+" value")

    #check assert values
    if int(asserts) < session['a']:
        return render_template('form.html',res="**asserts should be greater than $"+str(session['a']))

    #check time 10am to 5pm
    if 10 > int(time) or int(time) >17:
        return render_template('form.html',res="**appointments are allowed only during 10am to 5pm")

    #check date and time
    for i in appointment_data:
        i=dict(i)
        if i['owner']==owner:
            if date==i['date'] and time==i['time']:
                return render_template('form.html',res="**appointment time specified is already allocated to some other person")
        
    add={'owner':owner,'name':session['u']}
    add.update(data1)
    doc1.insert_one(add)
    return render_template('result.html')

@app.route('/booked')
def booked():
    doc1=client['doctors']['appointments']
    data=doc1.find()
    data2=[]
    for i in data:
        i=dict(i)
        if i['name'].lower()==session['u'].lower():
            data2.append(i)
    return render_template('appointments.html',data=data2,name='owner')

@app.route('/about')
def about():
    return render_template('1.html')

@app.route('/cancel',methods=['get'])
def cancel():
    i={}
    i[session['w']]=request.args.get('del')
    doc1=client['doctors']['appointments']
    print(i)
    doc1.delete_one(i)
    return render_template('appointments.html')

    
if __name__=='__main__':
    app.run()

