from datetime import date, datetime, timezone
from decimal import Decimal

from app import db


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    target_amount = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    current_amount = db.Column(
        db.Numeric(precision=10, scale=2), default=Decimal("0.00"), nullable=False
    )
    deadline = db.Column(db.Date, nullable=False)
    status = db.Column(
        db.String(20), default="active", nullable=False
    )  # active, completed, paused
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"<Goal {self.id}: {self.name} (${self.target_amount})>"

    @property
    def progress_percentage(self):
        """Calculate progress as a percentage"""
        if self.target_amount <= 0:
            return 0.0
        return float(min((self.current_amount / self.target_amount) * 100, 100))

    @property
    def remaining_amount(self):
        """Calculate remaining amount to reach goal"""
        return max(self.target_amount - self.current_amount, Decimal("0.00"))

    @property
    def is_completed(self):
        """Check if goal is completed"""
        return self.current_amount >= self.target_amount or self.status == "completed"

    @property
    def is_overdue(self):
        """Check if goal deadline has passed"""
        return date.today() > self.deadline and not self.is_completed

    @property
    def days_remaining(self):
        """Calculate days remaining until deadline"""
        if self.deadline <= date.today():
            return 0
        return (self.deadline - date.today()).days

    @property
    def formatted_target_amount(self):
        return f"${self.target_amount:,.2f}"

    @property
    def formatted_current_amount(self):
        return f"${self.current_amount:,.2f}"

    @property
    def formatted_remaining_amount(self):
        return f"${self.remaining_amount:,.2f}"

    def update_progress(self, amount):
        """Update current progress and check if goal is completed"""
        self.current_amount = max(Decimal(str(amount)), Decimal("0.00"))
        if self.current_amount >= self.target_amount and self.status == "active":
            self.status = "completed"
        elif self.current_amount < self.target_amount and self.status == "completed":
            self.status = "active"

    def add_progress(self, amount):
        """Add to current progress"""
        new_amount = self.current_amount + Decimal(str(amount))
        self.update_progress(new_amount)
