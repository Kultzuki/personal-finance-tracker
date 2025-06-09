from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    DecimalField,
    FloatField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError


class TransactionForm(FlaskForm):
    type = SelectField(
        "Transaction Type",
        choices=[("income", "Income"), ("expense", "Expense")],
        validators=[DataRequired(message="Please select a transaction type")],
    )

    description = StringField(
        "Description",
        validators=[
            DataRequired(message="Description is required"),
            Length(
                min=2,
                max=200,
                message="Description must be between 2 and 200 characters",
            ),
        ],
    )

    amount = DecimalField(
        "Amount ($)",
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

    category = SelectField(
        "Category",
        choices=[],
        validators=[DataRequired(message="Please select a category")],
    )

    date = DateField(
        "Transaction Date",
        validators=[DataRequired(message="Date is required")],
        default=datetime.today,
    )

    notes = TextAreaField(
        "Notes (Optional)",
        validators=[Length(max=500, message="Notes cannot exceed 500 characters")],
    )

    submit = SubmitField("Save Transaction")

    def validate_date(self, date_field):
        """Validate that date is not in the future"""
        if date_field.data > date.today():
            raise ValidationError("Transaction date cannot be in the future")

        # Don't allow dates older than 5 years
        from datetime import timedelta

        five_years_ago = date.today() - timedelta(days=365 * 5)
        if date_field.data < five_years_ago:
            raise ValidationError("Transaction date cannot be more than 5 years ago")

    def validate_amount(self, amount_field):
        """Additional amount validation"""
        if amount_field.data:
            try:
                # Ensure amount has at most 2 decimal places
                decimal_amount = Decimal(str(amount_field.data))
                if decimal_amount.as_tuple().exponent < -2:
                    raise ValidationError(
                        "Amount cannot have more than 2 decimal places"
                    )
            except (InvalidOperation, ValueError):
                raise ValidationError("Please enter a valid amount")

    def validate_category(self, category_field):
        """Validate category based on transaction type"""
        if self.type.data and category_field.data:
            valid_categories = []
            if self.type.data == "income":
                valid_categories = [choice[0] for choice in self.income_categories]
            elif self.type.data == "expense":
                valid_categories = [choice[0] for choice in self.expense_categories]

            if category_field.data not in [
                cat[1]
                for cat in (
                    self.income_categories
                    if self.type.data == "income"
                    else self.expense_categories
                )
            ]:
                raise ValidationError(
                    "Please select a valid category for this transaction type"
                )

    def __init__(self, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)

        # Define category choices based on transaction type
        self.income_categories = [
            ("salary", "Salary"),
            ("freelance", "Freelance"),
            ("business", "Business"),
            ("investment", "Investment"),
            ("gift", "Gift"),
            ("other_income", "Other Income"),
        ]

        self.expense_categories = [
            ("food", "Food & Dining"),
            ("transportation", "Transportation"),
            ("shopping", "Shopping"),
            ("entertainment", "Entertainment"),
            ("bills", "Bills & Utilities"),
            ("healthcare", "Healthcare"),
            ("education", "Education"),
            ("travel", "Travel"),
            ("housing", "Housing"),
            ("insurance", "Insurance"),
            ("other_expense", "Other Expense"),
        ]

        # Set default categories (will be updated via JavaScript)
        self.category.choices = self.expense_categories


class DeleteTransactionForm(FlaskForm):
    submit = SubmitField("Delete Transaction")
