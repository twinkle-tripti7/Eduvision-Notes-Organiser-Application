from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract
from authlib.integrations.flask_client import OAuth
import os
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure the upload directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)
oauth = OAuth(app)

# Google OAuth Setup

google = oauth.register(
    name="google",
    client_id = os.getenv("GOOGLE_CLIENT_ID"),
client_secret =os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url="https://oauth2.googleapis.com/token",
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    access_token_params=None,
    client_kwargs={
        "scope": "openid email profile",
    },
    jwks_uri="https://www.googleapis.com/oauth2/v3/certs"
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=True)

  

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    extracted_text = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=db.func.current_timestamp())


# Function to create user if not exists
def create_user(email, username):
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email, username=username)
        db.session.add(user)
        db.session.commit()
    return user

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Check if email is already registered
        existing_user = User.query.filter_by(username=email).first()
        if existing_user:
            flash('Email already registered! Try logging in.', 'error')
            return redirect(url_for('login'))

        # Create a new user with email & password
        new_user = User(username=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if not email or not password:
            flash('Please fill in all fields.', 'error')
            return redirect(url_for('login'))
        
        user = User.query.filter_by(username=email).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('login.html')



# Google Login Route
@app.route("/login/google")
def google_login():
    redirect_uri = url_for("google_authorized", _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/login/google/callback')
def google_authorized():
   try: 
    token = google.authorize_access_token()
    print("Google OAuth Token Response:", token)  # Debugging step
    if not token:
        flash("Failed to authenticate with Google!", "error")
        return redirect(url_for('login'))
    
    userinfo = google.get('https://www.googleapis.com/oauth2/v1/userinfo').json()
    print("User Info:", userinfo)
    
    email = userinfo.get("email")
    

    if not email:
        flash("Google did not provide an email!", "error")
        return redirect(url_for('login'))

    # Check if user exists
    user = User.query.filter_by(username=email).first()

    if user:
        session['user_id'] = user.id
        flash("Logged in successfully!", "success")
    else:
        # Register a new user
        new_user = User(username=email, password="None")  # No password needed for Google login
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        flash("Account created & logged in successfully!", "success")

    return redirect(url_for('index'))
   except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('login'))

    


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('google_token', None)  # Remove Google session
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        username = request.form['username']
        new_password = request.form['new_password']
        user = User.query.filter_by(username=username).first()

        if not user:
            flash('User not found!', 'error')
            return redirect(url_for('reset_password'))
        
        user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
        db.session.commit()
        flash('Password reset successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html')


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' not in session:
        flash('Please log in first!', 'error')
        return redirect(url_for('login'))
    
    search_query = request.args.get('search', '').strip()
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected!', 'error')
            return redirect(url_for('index'))
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected!', 'error')
            return redirect(url_for('index'))
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        extracted_text = pytesseract.image_to_string(Image.open(filepath))
        tags = request.form.get('tags', '')

        new_note = Note(user_id=session['user_id'], filename=filename, extracted_text=extracted_text, tags=tags)
        db.session.add(new_note)
        db.session.commit()

        flash('File uploaded and processed successfully!', 'success')
        return redirect(url_for('index'))
    
    if search_query:
        notes = Note.query.filter(
            (Note.tags.ilike(f"%{search_query}%")) |  # Search by tags
            (Note.extracted_text.ilike(f"%{search_query}%"))  # Search by text
        ).filter_by(user_id=session['user_id']).all()

        if not notes:
            flash("No results found for your search!", "error")
    else:
      notes = Note.query.filter_by(user_id=session['user_id']).all()
    return render_template('index.html', notes=notes)

@app.route('/edit/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    if 'user_id' not in session:
        flash('Please log in first!', 'error')
        return redirect(url_for('login'))
    
    note = Note.query.filter_by(id=note_id, user_id=session['user_id']).first()
    if not note:
        flash('Note not found!', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        note.extracted_text = request.form['extracted_text']
        note.tags = request.form['tags']
        db.session.commit()
        flash('Note updated successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('edit.html', note=note)

@app.route('/delete/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    if 'user_id' not in session:
        flash('Please log in first!', 'error')
        return redirect(url_for('login'))
    
    note = Note.query.filter_by(id=note_id, user_id=session['user_id']).first()
    if note:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], note.filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        
        db.session.delete(note)
        db.session.commit()
        flash('Note deleted successfully!', 'success')
    else:
        flash('Unauthorized action!', 'error')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)