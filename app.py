from flask import Flask,flash,request,redirect,render_template,session,url_for
from flask_mail import Mail,Message

import re
import bcrypt
import pymysql
import base64

app=Flask(__name__)
app.secret_key='nbnftaerswezxiuduwqd'

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=465
app.config['MAIL_USERNAME']='chegenelson@gmail.com'
app.config['MAIL_PASSWORD']='cfukaomufqorewgu'
app.config['MAIL_USE_TSL']=False
app.config['MAIL_USE_SSL']=True
mail=Mail(app)


connection=pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='flask_bb'
)


@app.route('/register',methods=['POST','GET'])
def register():
    if request.method=='POST':
        username=request.form['username']
        email=request.form['email']
        password=request.form['password']
        confirm=request.form['confirm']
        cur=connection.cursor()
        cur.execute('SELECT * FROM bad WHERE username=%s',(username))
        connection.commit()
        data=cur.fetchone()
        if username=='' or email=='' or password=='' or confirm=='':
            flash('All fields are required ','warning')
            return render_template('register.html',username=username,email=email,password=password,confirm=confirm)
        elif data is not None:
            flash('Create a new username the username is already created','warning')
            return render_template('register.html',username=username,email=email,password=password,confirm=confirm)
        elif username==password:
            flash('Username and password should not be similar','warning')
            return render_template('register.html',username=username,email=email,password=password,confirm=confirm)
        elif password != confirm:
            flash('Incorrect passwords','warning')
            return render_template('register.html',username=username,email=email,password=password,confirm=confirm)
        elif not re.search('[a-z]',password):
            flash('Password should have small characters','warning')
            return render_template('register.html',username=username,email=email,password=password,confirm=confirm)
        elif not re.search('[A-Z]',password):
            flash('Password should have capital letters','warning')
            return render_template('register.html',username=username,email=email,password=password,confirm=confirm)
        else:
            hashed_pwd=bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
            cur=connection.cursor()
            cur.execute('INSERT  INTO bad(username,email,password)VALUES(%s,%s,%s)',(username,email,hashed_pwd))
            connection.commit()
            subject='Account created'
            body='Thank you for creating an account with us'
            sendmail(subject,email,body)
            flash('Account successfully created','success')
            return redirect(url_for('login'))
    return render_template('register.html')

def sendmail(subject,email,body):
    try:
        msg=Message(subject=subject,sender='chegenelson641@gmail.com' ,recipients=[email] ,body=body)
        mail.send(msg)
    except Exception as a:
        print(a)


@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        if username=='' or password=='':
            flash('All fields are required','warning')
            return redirect(url_for('login'))
        else:
            cur=connection.cursor()
            cur.execute('SELECT * FROM bad WHERE username=%s',(username))
            connection.commit()
            data=cur.fetchone()
            if data is not None:
                if bcrypt.checkpw(password.encode('utf-8'),data[3].encode('utf-8')):
                    session['username']=data[1]
                    session['id']=data[0]
                    session['role']=data[4]
                    if session['role']=='user':
                        return redirect(url_for('home'))
                    else:
                        return redirect(url_for('home'))
                else:
                    flash('Incorrect password','warning')
                    return redirect(url_for('login'))
            else:
                flash('Incorrect username','warning')
                return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/product',methods=['POST','GET'])
def product():
    if request.method=='POST':
        name=request.form['name']
        description=request.form['description']
        amount=request.form['amount']
        image=request.files['image'].read()
        cur=connection.cursor()
        cur.execute('INSERT INTO mike(name,description,amount,image)VALUES(%s,%s,%s,%s)',(name,description,amount,image))
        connection.commit()
        return redirect(url_for('home'))
    return render_template('products.html')



@app.route('/manage')
def manage():
    cur=connection.cursor()
    cur.execute('SELECT * FROM mike')
    connection.commit()
    data=cur.fetchall()
    fetch=[]
    for team in data:
        image=team[4]
        decodedimage=base64.b64encode(image).decode('utf-8')
        uploadimage=list(team)
        uploadimage[4]=decodedimage
        fetch.append(uploadimage)
    return render_template('manage.html',fetch=fetch)



@app.route('/home')
def home():
    cur=connection.cursor()
    cur.execute('SELECT * FROM mike')
    connection.commit()
    data=cur.fetchall()
    fetch=[]
    for item in data:
        image=item[4]
        decodedimage=base64.b64encode(image).decode('utf-8')
        uploadimage=list(item)
        uploadimage[4]=decodedimage
        fetch.append(uploadimage)
        # return redirect(url_for('home'))
    return render_template('home.html',fetch=fetch)

@app.route('/update/<id>',methods=['POST','GET'])
def update(id):
    cur=connection.cursor()
    cur.execute('SELECT * FROM mike WHERE id=%s',(id))
    connection.commit()
    data=cur.fetchone()
    image=data[4]
    decodedimage=base64.b64encode(image).decode('utf-8')
    if request.method=='POST':
        name=request.form['name']
        description=request.form['description']
        amount=request.form['amount']
        image=request.files['image'].read()
        cur=connection.cursor()
        cur.execute('UPDATE mike SET name=%s,description=%s,amount=%s,image=%s WHERE id=%s',(name,description,amount,image,id))
        connection.commit()
        return redirect(url_for('manage'))
    return render_template('update.html',data=data,decodedimage=decodedimage)

@app.route('/delete/<id>')
def delete(id):
    cur=connection.cursor()
    cur.execute('DELETE  FROM mike WHERE id=%s',(id))
    connection.commit()
    return redirect(url_for('manage'))



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))






if __name__ in '__main__':
    app.run(debug=True)