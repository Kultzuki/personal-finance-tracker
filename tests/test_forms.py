"""Tests for WTForms forms."""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from app.forms.auth import LoginForm, RegistrationForm
from app.forms.goal import GoalForm, SetProgressForm, UpdateProgressForm
from app.forms.transaction import TransactionForm


class TestRegistrationForm:
    """Test RegistrationForm validation."""

    @pytest.mark.forms
    def test_valid_registration_form(self, app):
        """Test valid registration form."""
        with app.app_context():
            form = RegistrationForm(
                data={
                    "username": "testuser123",
                    "password": "TestPass123!",
                    "password2": "TestPass123!",
                }
            )

            assert form.validate()

    @pytest.mark.forms
    def test_username_validation(self, app):
        """Test username validation rules."""
        with app.app_context():
            # Test too short username
            form = RegistrationForm(
                data={
                    "username": "ab",
                    "password": "TestPass123!",
                    "password2": "TestPass123!",
                }
            )
            assert not form.validate()
            assert (
                "Username must be between 3 and 20 characters"
                in form.username.errors[0]
            )

            # Test too long username
            form = RegistrationForm(
                data={
                    "username": "a" * 25,
                    "password": "TestPass123!",
                    "password2": "TestPass123!",
                }
            )
            assert not form.validate()
            assert (
                "Username must be between 3 and 20 characters"
                in form.username.errors[0]
            )

            # Test invalid characters
            form = RegistrationForm(
                data={
                    "username": "test@user",
                    "password": "TestPass123!",
                    "password2": "TestPass123!",
                }
            )
            assert not form.validate()
            assert (
                "Username can only contain letters, numbers, and underscores"
                in form.username.errors[0]
            )

    @pytest.mark.forms
    def test_password_validation(self, app):
        """Test password validation rules."""
        with app.app_context():
            # Test too short password
            form = RegistrationForm(
                data={"username": "testuser", "password": "short", "password2": "short"}
            )
            assert not form.validate()
            assert (
                "Password must be at least 8 characters long" in form.password.errors[0]
            )

            # Test password without uppercase
            form = RegistrationForm(
                data={
                    "username": "testuser",
                    "password": "lowercase123!",
                    "password2": "lowercase123!",
                }
            )
            assert not form.validate()
            assert (
                "Password must contain at least one uppercase letter"
                in form.password.errors[0]
            )

            # Test password without lowercase
            form = RegistrationForm(
                data={
                    "username": "testuser",
                    "password": "UPPERCASE123!",
                    "password2": "UPPERCASE123!",
                }
            )
            assert not form.validate()
            assert (
                "Password must contain at least one lowercase letter"
                in form.password.errors[0]
            )

            # Test password without number
            form = RegistrationForm(
                data={
                    "username": "testuser",
                    "password": "TestPassword!",
                    "password2": "TestPassword!",
                }
            )
            assert not form.validate()
            assert (
                "Password must contain at least one number" in form.password.errors[0]
            )

            # Test password without special character
            form = RegistrationForm(
                data={
                    "username": "testuser",
                    "password": "TestPassword123",
                    "password2": "TestPassword123",
                }
            )
            assert not form.validate()
            assert (
                "Password must contain at least one special character"
                in form.password.errors[0]
            )

    @pytest.mark.forms
    def test_password_confirmation(self, app):
        """Test password confirmation validation."""
        with app.app_context():
            form = RegistrationForm(
                data={
                    "username": "testuser",
                    "password": "TestPass123!",
                    "password2": "DifferentPass123!",
                }
            )
            assert not form.validate()
            assert "Passwords must match" in form.password2.errors


class TestLoginForm:
    """Test LoginForm validation."""

    @pytest.mark.forms
    def test_valid_login_form(self, app):
        """Test valid login form."""
        with app.app_context():
            form = LoginForm(data={"username": "testuser", "password": "password123"})

            assert form.validate()

    @pytest.mark.forms
    def test_required_fields(self, app):
        """Test required field validation."""
        with app.app_context():
            form = LoginForm(data={"username": "", "password": ""})

            assert not form.validate()
            assert "Username is required" in form.username.errors[0]
            assert "Password is required" in form.password.errors[0]

    @pytest.mark.forms
    def test_username_length_validation(self, app):
        """Test username length validation."""
        with app.app_context():
            form = LoginForm(
                data={"username": "ab", "password": "password123"}  # Too short
            )

            assert not form.validate()
            assert "Please enter a valid username" in form.username.errors[0]


class TestTransactionForm:
    """Test TransactionForm validation."""

    @pytest.mark.forms
    def test_valid_transaction_form(self, app):
        """Test valid transaction form."""
        with app.app_context():
            form = TransactionForm(
                data={
                    "type": "expense",
                    "description": "Grocery shopping",
                    "amount": Decimal("125.50"),
                    "category": "food",
                    "date": date.today(),
                    "notes": "Weekly groceries",
                }
            )

            # Set category choices for validation
            form.category.choices = form.expense_categories

            assert form.validate()

    @pytest.mark.forms
    def test_required_fields(self, app):
        """Test required field validation."""
        with app.app_context():
            form = TransactionForm(
                data={
                    "type": "",
                    "description": "",
                    "amount": None,
                    "category": "",
                    "date": None,
                }
            )

            assert not form.validate()
            assert "Please select a transaction type" in form.type.errors[0]
            assert "Description is required" in form.description.errors[0]
            assert "Amount is required" in form.amount.errors[0]
            assert "Please select a category" in form.category.errors[0]
            assert "Date is required" in form.date.errors[0]

    @pytest.mark.forms
    def test_description_validation(self, app):
        """Test description validation."""
        with app.app_context():
            # Test too short description
            form = TransactionForm(
                data={
                    "type": "expense",
                    "description": "A",  # Too short
                    "amount": Decimal("125.50"),
                    "category": "food",
                    "date": date.today(),
                }
            )

            assert not form.validate()
            assert (
                "Description must be between 2 and 200 characters"
                in form.description.errors[0]
            )

            # Test too long description
            form = TransactionForm(
                data={
                    "type": "expense",
                    "description": "A" * 201,  # Too long
                    "amount": Decimal("125.50"),
                    "category": "food",
                    "date": date.today(),
                }
            )

            assert not form.validate()
            assert (
                "Description must be between 2 and 200 characters"
                in form.description.errors[0]
            )

    @pytest.mark.forms
    def test_amount_validation(self, app):
        """Test amount validation."""
        with app.app_context():
            # Test negative amount
            form = TransactionForm(
                data={
                    "type": "expense",
                    "description": "Test transaction",
                    "amount": Decimal("-10.00"),
                    "category": "food",
                    "date": date.today(),
                }
            )

            assert not form.validate()
            assert (
                "Amount must be between $0.01 and $999,999.99" in form.amount.errors[0]
            )

            # Test zero amount
            form = TransactionForm(
                data={
                    "type": "expense",
                    "description": "Test transaction",
                    "amount": Decimal("0.00"),
                    "category": "food",
                    "date": date.today(),
                }
            )

            assert not form.validate()
            assert (
                "Amount must be between $0.01 and $999,999.99" in form.amount.errors[0]
            )

            # Test too large amount
            form = TransactionForm(
                data={
                    "type": "expense",
                    "description": "Test transaction",
                    "amount": Decimal("1000000.00"),
                    "category": "food",
                    "date": date.today(),
                }
            )

            assert not form.validate()
            assert (
                "Amount must be between $0.01 and $999,999.99" in form.amount.errors[0]
            )

    @pytest.mark.forms
    def test_date_validation(self, app):
        """Test date validation."""
        with app.app_context():
            # Test future date
            form = TransactionForm(
                data={
                    "type": "expense",
                    "description": "Test transaction",
                    "amount": Decimal("125.50"),
                    "category": "food",
                    "date": date.today() + timedelta(days=1),
                }
            )

            form.category.choices = form.expense_categories

            assert not form.validate()
            assert "Transaction date cannot be in the future" in form.date.errors[0]

            # Test date too far in the past
            form = TransactionForm(
                data={
                    "type": "expense",
                    "description": "Test transaction",
                    "amount": Decimal("125.50"),
                    "category": "food",
                    "date": date.today() - timedelta(days=365 * 6),  # 6 years ago
                }
            )

            form.category.choices = form.expense_categories

            assert not form.validate()
            assert (
                "Transaction date cannot be more than 5 years ago"
                in form.date.errors[0]
            )

    @pytest.mark.forms
    def test_notes_validation(self, app):
        """Test notes validation."""
        with app.app_context():
            form = TransactionForm(
                data={
                    "type": "expense",
                    "description": "Test transaction",
                    "amount": Decimal("125.50"),
                    "category": "food",
                    "date": date.today(),
                    "notes": "A" * 501,  # Too long
                }
            )

            form.category.choices = form.expense_categories

            assert not form.validate()
            assert "Notes cannot exceed 500 characters" in form.notes.errors[0]


class TestGoalForm:
    """Test GoalForm validation."""

    @pytest.mark.forms
    def test_valid_goal_form(self, app):
        """Test valid goal form."""
        with app.app_context():
            form = GoalForm(
                data={
                    "name": "Emergency Fund",
                    "description": "Build emergency savings",
                    "target_amount": Decimal("10000.00"),
                    "current_amount": Decimal("2500.00"),
                    "deadline": date.today() + timedelta(days=365),
                    "status": "active",
                }
            )

            assert form.validate()

    @pytest.mark.forms
    def test_required_fields(self, app):
        """Test required field validation."""
        with app.app_context():
            form = GoalForm(
                data={"name": "", "target_amount": None, "deadline": None, "status": ""}
            )

            assert not form.validate()
            assert "Goal name is required" in form.name.errors[0]
            assert "Target amount is required" in form.target_amount.errors[0]
            assert "Target date is required" in form.deadline.errors[0]
            assert "Please select a status" in form.status.errors[0]

    @pytest.mark.forms
    def test_name_validation(self, app):
        """Test goal name validation."""
        with app.app_context():
            # Test too short name
            form = GoalForm(
                data={
                    "name": "AB",
                    "target_amount": Decimal("1000.00"),
                    "deadline": date.today() + timedelta(days=30),
                    "status": "active",
                }
            )

            assert not form.validate()
            assert (
                "Goal name must be between 3 and 100 characters" in form.name.errors[0]
            )

            # Test whitespace-only name
            form = GoalForm(
                data={
                    "name": "   ",
                    "target_amount": Decimal("1000.00"),
                    "deadline": date.today() + timedelta(days=30),
                    "status": "active",
                }
            )

            assert not form.validate()
            assert (
                "Goal name cannot be empty or contain only spaces"
                in form.name.errors[0]
            )

    @pytest.mark.forms
    def test_target_amount_validation(self, app):
        """Test target amount validation."""
        with app.app_context():
            # Test too small amount
            form = GoalForm(
                data={
                    "name": "Test Goal",
                    "target_amount": Decimal("0.50"),
                    "deadline": date.today() + timedelta(days=30),
                    "status": "active",
                }
            )

            assert not form.validate()
            assert (
                "Target amount must be between $1.00 and $9,999,999.99"
                in form.target_amount.errors[0]
            )

            # Test too large amount
            form = GoalForm(
                data={
                    "name": "Test Goal",
                    "target_amount": Decimal("10000000.00"),
                    "deadline": date.today() + timedelta(days=30),
                    "status": "active",
                }
            )

            assert not form.validate()
            assert (
                "Target amount must be between $1.00 and $9,999,999.99"
                in form.target_amount.errors[0]
            )

    @pytest.mark.forms
    def test_current_amount_validation(self, app):
        """Test current amount validation."""
        with app.app_context():
            # Test negative current amount
            form = GoalForm(
                data={
                    "name": "Test Goal",
                    "target_amount": Decimal("1000.00"),
                    "current_amount": Decimal("-100.00"),
                    "deadline": date.today() + timedelta(days=30),
                    "status": "active",
                }
            )

            assert not form.validate()
            assert "Current amount cannot be negative" in form.current_amount.errors[0]

            # Test current amount exceeding target
            form = GoalForm(
                data={
                    "name": "Test Goal",
                    "target_amount": Decimal("1000.00"),
                    "current_amount": Decimal("1500.00"),
                    "deadline": date.today() + timedelta(days=30),
                    "status": "active",
                }
            )

            assert not form.validate()
            assert (
                "Current progress cannot exceed the target amount"
                in form.current_amount.errors[0]
            )

    @pytest.mark.forms
    def test_deadline_validation(self, app):
        """Test deadline validation."""
        with app.app_context():
            # Test past deadline
            form = GoalForm(
                data={
                    "name": "Test Goal",
                    "target_amount": Decimal("1000.00"),
                    "deadline": date.today() - timedelta(days=1),
                    "status": "active",
                }
            )

            assert not form.validate()
            assert "Target date must be in the future" in form.deadline.errors[0]

            # Test deadline too far in future
            form = GoalForm(
                data={
                    "name": "Test Goal",
                    "target_amount": Decimal("1000.00"),
                    "deadline": date.today() + timedelta(days=365 * 25),  # 25 years
                    "status": "active",
                }
            )

            assert not form.validate()
            assert (
                "Target date cannot be more than 20 years in the future"
                in form.deadline.errors[0]
            )

            # Test deadline too soon
            form = GoalForm(
                data={
                    "name": "Test Goal",
                    "target_amount": Decimal("1000.00"),
                    "deadline": date.today() + timedelta(days=3),  # 3 days
                    "status": "active",
                }
            )

            assert not form.validate()
            assert (
                "Consider setting a target date at least one week from now"
                in form.deadline.errors[0]
            )

    @pytest.mark.forms
    def test_description_validation(self, app):
        """Test description validation."""
        with app.app_context():
            form = GoalForm(
                data={
                    "name": "Test Goal",
                    "description": "A" * 501,  # Too long
                    "target_amount": Decimal("1000.00"),
                    "deadline": date.today() + timedelta(days=30),
                    "status": "active",
                }
            )

            assert not form.validate()
            assert (
                "Description cannot exceed 500 characters" in form.description.errors[0]
            )


class TestUpdateProgressForm:
    """Test UpdateProgressForm validation."""

    @pytest.mark.forms
    def test_valid_update_progress_form(self, app):
        """Test valid update progress form."""
        with app.app_context():
            form = UpdateProgressForm(data={"amount": Decimal("250.00")})

            assert form.validate()

    @pytest.mark.forms
    def test_required_amount(self, app):
        """Test required amount field."""
        with app.app_context():
            form = UpdateProgressForm(data={"amount": None})

            assert not form.validate()
            assert "Amount is required" in form.amount.errors[0]

    @pytest.mark.forms
    def test_amount_range_validation(self, app):
        """Test amount range validation."""
        with app.app_context():
            # Test too small amount
            form = UpdateProgressForm(data={"amount": Decimal("0.00")})

            assert not form.validate()
            assert (
                "Amount must be between $0.01 and $999,999.99" in form.amount.errors[0]
            )

            # Test too large amount
            form = UpdateProgressForm(data={"amount": Decimal("1000000.00")})

            assert not form.validate()
            assert (
                "Amount must be between $0.01 and $999,999.99" in form.amount.errors[0]
            )


class TestSetProgressForm:
    """Test SetProgressForm validation."""

    @pytest.mark.forms
    def test_valid_set_progress_form(self, app):
        """Test valid set progress form."""
        with app.app_context():
            form = SetProgressForm(data={"current_amount": Decimal("750.00")})

            assert form.validate()

    @pytest.mark.forms
    def test_required_current_amount(self, app):
        """Test required current amount field."""
        with app.app_context():
            form = SetProgressForm(data={"current_amount": None})

            assert not form.validate()
            assert "Progress amount is required" in form.current_amount.errors[0]

    @pytest.mark.forms
    def test_current_amount_range_validation(self, app):
        """Test current amount range validation."""
        with app.app_context():
            # Test negative amount
            form = SetProgressForm(data={"current_amount": Decimal("-100.00")})

            assert not form.validate()
            assert "Progress cannot be negative" in form.current_amount.errors[0]

            # Test too large amount
            form = SetProgressForm(data={"current_amount": Decimal("10000000.00")})

            assert not form.validate()
            assert (
                "Progress cannot be negative or exceed $9,999,999.99"
                in form.current_amount.errors[0]
            )
