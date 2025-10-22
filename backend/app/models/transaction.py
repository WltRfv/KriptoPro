from .. import db
from datetime import datetime
import uuid


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    wallet_id = db.Column(db.String(36), db.ForeignKey('wallets.id'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'send', 'receive', 'swap'
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    to_address = db.Column(db.String(255))  # For send transactions
    from_address = db.Column(db.String(255))  # For receive transactions
    tx_hash = db.Column(db.String(255))  # Blockchain transaction hash
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, failed
    fee = db.Column(db.Float, default=0.0)
    block_height = db.Column(db.Integer)
    confirmations = db.Column(db.Integer, default=0)

    # Multi-signature fields
    required_signatures = db.Column(db.Integer, default=1)
    collected_signatures = db.Column(db.Integer, default=0)
    signature_data = db.Column(db.Text)  # JSON with signature details

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Правильное отношение - используем back_populates
    wallet = db.relationship('Wallet', back_populates='transactions')