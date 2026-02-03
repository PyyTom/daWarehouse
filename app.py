from flask import Flask,redirect,url_for,render_template,request,session
from flask_mail import Mail,Message
import sqlite3,datetime,secrets
app=Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_mail_address@gmail.com'
app.config['MAIL_PASSWORD'] = '****************'
mail = Mail(app)
app.secret_key='secret_password'
@app.route('/')
def home():
    return redirect(url_for('sales'))
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        name=request.form['name'].strip().upper()
        db=sqlite3.connect('db.db')
        user=db.execute('select MAIL from CLIENTS where NAME=?',(name,)).fetchone()
        db.close()
        if not user:return render_template('login.html',error='Invalid credentials')
        email=user[0]
        token=secrets.token_hex(8)
        session['pending_name']=name
        session['pending_token']=token
        msg=Message('Your access-token',sender='tommyacha@gmail.com',recipients=[email])
        msg.body=f'Hello {name}, your access-token is: {session["pending_token"]}'
        mail.send(msg)
        return redirect('/token')
    return render_template('login.html')
@app.route('/token',methods=['GET','POST'])
def token():
    if request.method=='POST':
        token=request.form['token']
        expected = session.get('pending_token') 
        name = session.get('pending_name')
        if not expected or not name:return render_template('token.html', error='No token pending. Please log in again.')
        if token!=expected:return render_template('token.html',error='Invalid token')
        session['client']=name
        session.pop('pending_token')
        session.pop('pending_name')
        return redirect('/sales')
    return render_template('token.html')
@app.route('/sales')
def sales():
    if 'client' not in session:return redirect('/login')
    db = sqlite3.connect('db.db')
    products = db.execute('SELECT SUPPLIER, NAME, PRICE, STOCK FROM PRODUCTS WHERE STOCK > 0 ORDER BY SUPPLIER, NAME').fetchall()
    db.close()
    return render_template('sales.html', products=products, client=session['client'])
@app.route('/sell', methods=['POST'])
def sell():
    if 'client' not in session:return redirect('/login')
    client = session['client']
    raw = request.form['product']
    supplier, product = raw.split('||')
    qty = int(request.form['qty'])
    db = sqlite3.connect('db.db')
    price = db.execute('SELECT PRICE FROM PRODUCTS WHERE SUPPLIER=? and NAME=?',(supplier, product)).fetchone()[0]
    partial=price*qty
    db.execute('INSERT INTO SALES VALUES (?,?,?,?,?)',(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),client,product,partial,qty))
    db.commit()
    db.execute('UPDATE PRODUCTS SET STOCK = STOCK - ? WHERE SUPPLIER=? AND NAME=?',(qty, supplier, product))
    db.commit()
    db.close()
    return render_template('sold.html', client=client, items=[(product, qty)])
if __name__=='__main__':app.run(debug=True)
