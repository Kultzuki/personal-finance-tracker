from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation

from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    DecimalField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    NumberRange,
    Optional,
    ValidationError,
)


class GoalForm(FlaskForm):
    name = StringField(
        "Goal Name",
        validators=[
            DataRequired(message="Goal name is required"),
            Length(
                min=3, max=100, message="Goal name must be between 3 and 100 characters"
            ),
        ],
    )

    description = TextAreaField(
        "Description (Optional)",
        validators=[
            Optional(),
            Length(max=500, message="Description cannot exceed 500 characters"),
        ],
    )

    target_amount = DecimalField(
        "Target Amount ($)",
        validators=[
            DataRequired(message="Target amount is required"),
            NumberRange(
                min=1.00,
                max=9999999.99,
                message="Target amount must be between $1.00 and $9,999,999.99",
            ),
        ],
        places=2,
    )

    current_amount = DecimalField(
        "Current Progress ($)",
        validators=[
            Optional(),
            NumberRange(
                min=0,
                max=9999999.99,
                message="Current amount cannot be negative or exceed $9,999,999.99",
            ),
        ],
        places=2,
        default=0.0,
    )

    deadline = DateField(
        "Target Date", validators=[DataRequired(message="Target date is required")]
    )

    status = SelectField(
        "Status",
        choices=[
            ("active", "Active"),
            ("paused", "Paused"),
            ("completed", "Completed"),
        ],
        default="active",
        validators=[DataRequired(message="Please select a status")],
    )

    submit = SubmitField("Save Goal")

    def validate_deadline(self, deadline):
        """Validate deadline is in the future and reasonable"""
        if not deadline.data:
            return

        today = date.today()
        if deadline.data <= today:
            raise ValidationError("Target date must be in the future")

        # Don't allow deadlines more than 20 years in the future
        max_date = today + timedelta(days=365 * 20)
        if deadline.data > max_date:
            raise ValidationError(
                "Target date cannot be more than 20 years in the future"
            )

        # Warn if deadline is very soon (less than 7 days)
        week_from_now = today + timedelta(days=7)
        if deadline.data < week_from_now:
            raise ValidationError(
                "Consider setting a target date at least one week from now for realistic planning"
            )

    def validate_current_amount(self, current_amount):
        """Validate current amount against target amount"""
        if not current_amount.data or not self.target_amount.data:
            return

        if current_amount.data > self.target_amount.data:
            raise ValidationError("Current progress cannot exceed the target amount")

    def validate_target_amount(self, target_amount):
        """Additional target amount validation"""
        if target_amount.data:
            try:
                # Ensure amount has at most 2 decimal places
                decimal_amount = Decimal(str(target_amount.data))
                if decimal_amount.as_tuple().exponent < -2:
                    raise ValidationError(
                        "Amount cannot have more than 2 decimal places"
                    )
            except (InvalidOperation, ValueError):
                raise ValidationError("Please enter a valid target amount")

    def validate_name(self, name):
        """Validate goal name doesn't contain only whitespace"""
        if name.data and not name.data.strip():
            raise ValidationError("Goal name cannot be empty or contain only spaces")


class UpdateProgressForm(FlaskForm):
    amount = DecimalField(
        "Amount to Add ($)",
        validators=[
            DataRequired(message="Amount is required"),
            NumberRange(
                min=0.01,
                max=999999.99,
                message="Amount must be between $0.01 and $999,999.99",
            ),
        ],
        places=2,
    )

    submit = SubmitField("Add Progress")

    def validate_amount(self, amount_field):
        """Validate amount format"""
        if amount_field.data:
            try:
                decimal_amount = Decimal(str(amount_field.data))
                if decimal_amount.as_tuple().exponent < -2:
                    raise ValidationError(
                        "Amount cannot have more than 2 decimal places"
                    )
            except (InvalidOperation, ValueError):
                raise ValidationError("Please enter a valid amount")


class SetProgressForm(FlaskForm):
    current_amount = DecimalField(
        "Set Current Progress ($)",
        validators=[
            DataRequired(message="Progress amount is required"),
            NumberRange(
                min=0,
                max=9999999.99,
                message="Progress cannot be negative or exceed $9,999,999.99",
            ),
        ],
        places=2,
    )

    submit = SubmitField("Update Progress")

    def validate_current_amount(self, current_amount_field):
        """Validate current amount format"""
        if current_amount_field.data:
            try:
                decimal_amount = Decimal(str(current_amount_field.data))
                if decimal_amount.as_tuple().exponent < -2:
                    raise ValidationError(
                        "Amount cannot have more than 2 decimal places"
                    )
            except (InvalidOperation, ValueError):
                raise ValidationError("Please enter a valid progress amount")


class DeleteGoalForm(FlaskForm):
    submit = SubmitField("Delete Goal")
