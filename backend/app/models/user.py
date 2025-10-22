from .. import db
from datetime import datetime
import uuid
import bcrypt

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # MFA fields
    totp_secret = db.Column(db.String(32))
    backup_codes = db.Column(db.Text)  # JSON string of backup codes
    webauthn_credentials = db.Column(db.Text)  # JSON string of WebAuthn credentials
    
    # Security settings
    login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)
    
    # Relationships
    key_shards = db.relationship('KeyShard', backref='user', lazy=True, cascade='all, delete-orphan')
    login_history = db.relationship('LoginAttempt', backref='user', lazy=True)
    wallets = db.relationship('Wallet', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def is_locked(self):
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False

class KeyShard(db.Model):
    __tablename__ = 'key_shards'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    shard_data = db.Column(db.Text, nullable=False)  # Encrypted shard
    shard_index = db.Column(db.Integer, nullable=False)  # Which shard this is (1-4)
    recipient_email = db.Column(db.String(120), nullable=False)  # Email of team member
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime)

class LoginAttempt(db.Model):
    __tablename__ = 'login_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    attempt_type = db.Column(db.String(50), nullable=False)  # 'password', 'totp', 'shard', 'webauthn'
    is_successful = db.Column(db.Boolean, default=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Wallet(db.Model):
    __tablename__ = 'wallets'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    currency = db.Column(db.String(10), nullable=False, default='BTC')  # BTC, ETH, etc.
    address = db.Column(db.String(255), nullable=False)
    private_key_encrypted = db.Column(db.Text, nullable=False)  # Encrypted private key
    balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Правильное отношение с back_populates
    transactions = db.relationship('Transaction', back_populates='wallet', lazy=True, cascade='all, delete-orphan')