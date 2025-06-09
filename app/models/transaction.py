from datetime import datetime, timezone
from decimal import Decimal

from app import db


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10), nullable=False)  # 'income' or 'expense'
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    date = db.Column(
        db.Date, nullable=False, default=lambda: datetime.now(timezone.utc).date()
    )
    description = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"<Transaction {self.id}: {self.type} ${self.amount}>"

    @property
    def formatted_amount(self):
        return f"${self.amount:,.2f}"

    @property
    def is_income(self):
        return self.type == "income"

    @property
    def is_expense(self):
        return self.type == "expense"
