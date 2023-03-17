from flask import Flask, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

f = open('userid.txt', 'w')
f.close()

def writeFile(string):
    f = open('userid.txt', 'w')
    f.write(string)
    f.close()

def readFile():
    f = open('userid.txt', 'r')
    v=f.readline()
    return int(v)

def ClearFile():
    f= open('userid.txt','w')
    f.seek(0) 
    f.truncate() 

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
db = SQLAlchemy(app)
class User(db.Model):
    __tableName__='user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120))

class Note(db.Model):
    user_id=db.Column(db.ForeignKey("user.id"))
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text)
with app.app_context():
    db.create_all()
with app.app_context():
    users=User.query.all()

@app.route('/')
def landing():    
    return render_template('index.html')
@app.route('/notes')
def notes():
    userId=readFile()
    notes=Note.query.filter_by(user_id=userId).all()
    return render_template('notes.html',note=notes)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            return "User already exists"
        hashed_password = generate_password_hash(password)
        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        user = User.query.filter_by(username=username).first()
        userId=str(user.id)
        writeFile(userId)
        return redirect('/notes')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_exists = User.query.filter_by(username=username).first()
        if not user_exists or not check_password_hash(user_exists.password,password):
            return "Invalid credentials"
        user= User.query.filter_by(username=username).first()
        userId=str(user.id)
        writeFile(userId)
        return redirect('/notes')
    
    return render_template('login.html')

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        userId=readFile()
        note = Note(user_id=userId,title=title, content=content)
        db.session.add(note)
        db.session.commit()
        return redirect('/notes')
    return render_template('create.html')
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    note = Note.query.get(id)
    if request.method == 'POST':
        note.title = request.form['title']
        note.content = request.form['content']
        db.session.commit()
        return redirect('/notes')
    return render_template('update.html', note=note)
@app.route('/delete/<int:id>')
def delete(id):
    note = Note.query.get(id)
    db.session.delete(note)
    db.session.commit()
    return redirect('/notes')
@app.route('/signout')
def signout():
    ClearFile()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
    userId=''