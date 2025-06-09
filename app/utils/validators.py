"""Custom validators for forms and data validation."""

import re
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from typing import Optional

from wtforms import ValidationError


class CustomValidators:
    """Collection of custom validation functions."""

    @staticmethod
    def validate_username(form, field):
        """Validate username format and length."""
        username = field.data

        if len(username) < 3 or len(username) > 20:
            raise ValidationError("Username must be between 3 and 20 characters long.")

        if not re.match(r"^[a-zA-Z0-9_]+$", username):
            raise ValidationError(
                "Username can only contain letters, numbers, and underscores."
            )

    @staticmethod
    def validate_strong_password(form, field):
        """Validate password strength requirements."""
        password = field.data

        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")

        if not re.search(r"[A-Z]", password):
            raise ValidationError(
                "Password must contain at least one uppercase letter."
            )

        if not re.search(r"[a-z]", password):
            raise ValidationError(
                "Password must contain at least one lowercase letter."
            )

        if not re.search(r"\d", password):
            raise ValidationError("Password must contain at least one number.")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                "Password must contain at least one special character."
            )

    @staticmethod
    def validate_decimal_range(min_value: Decimal, max_value: Decimal):
        """Create a validator for decimal range validation."""

        def validator(form, field):
            if field.data is None:
                return

            try:
                value = Decimal(str(field.data))
                if value < min_value or value > max_value:
                    raise ValidationError(
                        f"Amount must be between ${min_value:,.2f} and ${max_value:,.2f}"
                    )
            except (InvalidOperation, TypeError):
                raise ValidationError("Invalid amount format.")

        return validator

    @staticmethod
    def validate_decimal_precision(precision: int = 2):
        """Create a validator for decimal precision."""

        def validator(form, field):
            if field.data is None:
                return

            try:
                decimal_value = Decimal(str(field.data))
                if decimal_value.as_tuple().exponent < -precision:
                    raise ValidationError(
                        f"Amount cannot have more than {precision} decimal places."
                    )
            except (InvalidOperation, TypeError):
                raise ValidationError("Invalid amount format.")

        return validator

    @staticmethod
    def validate_future_date(form, field):
        """Validate that the date is in the future."""
        if field.data and field.data <= date.today():
            raise ValidationError("Target date must be in the future.")

    @staticmethod
    def validate_date_range(min_days: int = 7, max_years: int = 20):
        """Create a validator for date range."""

        def validator(form, field):
            if field.data is None:
                return

            today = date.today()
            min_date = today + timedelta(days=min_days)
            max_date = today + timedelta(days=max_years * 365)

            if field.data < today:
                raise ValidationError("Target date must be in the future.")

            if field.data > max_date:
                raise ValidationError(
                    f"Target date cannot be more than {max_years} years in the future."
                )

            if field.data < min_date:
                raise ValidationError(
                    f"Consider setting a target date at least {min_days} days from now."
                )

        return validator

    @staticmethod
    def validate_transaction_date(form, field):
        """Validate transaction date range."""
        if field.data is None:
            return

        today = date.today()
        min_date = today - timedelta(days=5 * 365)  # 5 years ago

        if field.data > today:
            raise ValidationError("Transaction date cannot be in the future.")

        if field.data < min_date:
            raise ValidationError("Transaction date cannot be more than 5 years ago.")

    @staticmethod
    def validate_goal_current_amount(form, field):
        """Validate that current amount doesn't exceed target amount."""
        if field.data is None:
            return

        if field.data < 0:
            raise ValidationError("Current amount cannot be negative.")

        # Check if target_amount field exists and has data
        if hasattr(form, "target_amount") and form.target_amount.data:
            try:
                current = Decimal(str(field.data))
                target = Decimal(str(form.target_amount.data))

                if current > target:
                    raise ValidationError(
                        "Current progress cannot exceed the target amount."
                    )
            except (InvalidOperation, TypeError):
                pass  # Let other validators handle invalid format

    @staticmethod
    def validate_whitespace_only(form, field):
        """Validate that field is not empty or whitespace only."""
        if field.data and not field.data.strip():
            raise ValidationError(
                f"{field.label.text} cannot be empty or contain only spaces."
            )

    @staticmethod
    def validate_description_length(min_length: int = 2, max_length: int = 200):
        """Create a validator for description length."""

        def validator(form, field):
            if field.data is None:
                return

            text = field.data.strip()
            if len(text) < min_length or len(text) > max_length:
                raise ValidationError(
                    f"Description must be between {min_length} and {max_length} characters."
                )

        return validator

    @staticmethod
    def validate_goal_name_length(min_length: int = 3, max_length: int = 100):
        """Create a validator for goal name length."""

        def validator(form, field):
            if field.data is None:
                return

            text = field.data.strip()
            if len(text) < min_length or len(text) > max_length:
                raise ValidationError(
                    f"Goal name must be between {min_length} and {max_length} characters."
                )

        return validator


class TransactionValidators:
    """Specialized validators for transaction forms."""

    @staticmethod
    def validate_category_for_type(form, field):
        """Validate that category matches transaction type."""
        if not field.data or not hasattr(form, "type") or not form.type.data:
            return

        income_categories = [
            "salary",
            "freelance",
            "investment",
            "bonus",
            "gift",
            "other_income",
        ]
        expense_categories = [
            "food",
            "transportation",
            "shopping",
            "entertainment",
            "bills",
            "healthcare",
            "education",
            "travel",
            "other_expense",
        ]

        transaction_type = form.type.data
        category = field.data

        if transaction_type == "income" and category not in income_categories:
            raise ValidationError("Invalid category for income transaction.")
        elif transaction_type == "expense" and category not in expense_categories:
            raise ValidationError("Invalid category for expense transaction.")


class GoalValidators:
    """Specialized validators for goal forms."""

    @staticmethod
    def validate_goal_deadline(form, field):
        """Comprehensive goal deadline validation."""
        if field.data is None:
            return

        today = date.today()

        # Must be in the future
        if field.data <= today:
            raise ValidationError("Target date must be in the future.")

        # Not too far in the future (20 years max)
        max_date = today + timedelta(days=20 * 365)
        if field.data > max_date:
            raise ValidationError(
                "Target date cannot be more than 20 years in the future."
            )

        # Warning for very short-term goals (less than 7 days)
        min_recommended_date = today + timedelta(days=7)
        if field.data < min_recommended_date:
            raise ValidationError(
                "Consider setting a target date at least one week from now for better planning."
            )

    @staticmethod
    def validate_progress_amount_range(form, field):
        """Validate progress amount for goal updates."""
        if field.data is None:
            return

        try:
            amount = Decimal(str(field.data))
            min_amount = Decimal("0.01")
            max_amount = Decimal("9999999.99")

            if amount < min_amount or amount > max_amount:
                raise ValidationError(
                    f"Amount must be between ${min_amount} and ${max_amount:,.2f}"
                )
        except (InvalidOperation, TypeError):
            raise ValidationError("Invalid amount format.")

    @staticmethod
    def validate_current_progress_range(form, field):
        """Validate current progress amount for goal setting."""
        if field.data is None:
            return

        try:
            amount = Decimal(str(field.data))

            if amount < 0:
                raise ValidationError("Progress cannot be negative.")

            max_amount = Decimal("9999999.99")
            if amount > max_amount:
                raise ValidationError(
                    f"Progress cannot be negative or exceed ${max_amount:,.2f}"
                )
        except (InvalidOperation, TypeError):
            raise ValidationError("Invalid amount format.")
