from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
db = SQLAlchemy(app)

# Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    birthday = db.Column(db.Date)  
    address = db.Column(db.String(200))
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    image_filename = db.Column(db.String(100), nullable=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        file = request.files['image']
        filename = None

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(f"{app.config['UPLOAD_FOLDER']}/{filename}")

        birthday = datetime.strptime(request.form['birthday'], '%Y-%m-%d').date()

        hashed_pw = generate_password_hash(request.form['password'])
        user = User(
            name=request.form['name'],
            birthday=birthday,
            address=request.form['address'],
            username=request.form['username'],
            password=hashed_pw,
            image_filename=filename
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user_id'] = user.id
            return redirect(url_for('user_home'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/user')
def user_home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])

    # 🔢 Calculate age from birthday
    today = date.today()
    age = today.year - user.birthday.year - ((today.month, today.day) < (user.birthday.month, user.birthday.day))

    return render_template('user_home.html', user=user, age=age)





if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
