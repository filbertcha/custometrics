# __init__.py (Perbaikan dengan relasi user yang lebih jelas)
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin
from sqlalchemy.sql import func
from sqlalchemy import func
import pytz
from datetime import datetime

# Mendapatkan timezone Asia/Jakarta
jakarta_tz = pytz.timezone('Asia/Jakarta')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///datasetScraping2.db'
app.config['SECRET_KEY'] = '89f577632ad9952ba7b30630'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login_page"
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    # Relasi dengan DataScraping, cascade untuk menghapus data ketika user dihapus
    data_scraping = db.relationship('DataScraping', backref='owner', lazy=True, cascade="all, delete-orphan")
    
    @property
    def password(self):
        return self.password
        
    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')
    
    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

class DataScraping(db.Model):



    id = db.Column(db.Integer(), primary_key=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(jakarta_tz))
    link = db.Column(db.String(length=2000), nullable=False)
    prompt = db.Column(db.Text, nullable=True)  # Menggunakan Text untuk data besar
    response = db.Column(db.Text, nullable=True)  # Menggunakan Text untuk data besar
    prompt_preprocessing = db.Column(db.Text, nullable=True)
    response_preprocessing = db.Column(db.Text, nullable=True)
    owner_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    owner_username = db.Column(db.String(length=30), nullable=False)
    
    def __repr__(self):
        return f'Data scraping dari {self.owner_username} - Link: {self.link[:30]}...'

# Import routes di akhir untuk menghindari circular import
from routes import *