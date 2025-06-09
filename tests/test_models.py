"""Tests for data models."""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from app.models.goal import Goal
from app.models.transaction import Transaction
from app.models.user import User


class TestUser:
    """Test User model."""

    @pytest.mark.models
    def test_user_creation(self, app):
        """Test user creation."""
        with app.app_context():
            user = User(username="testuser")
            user.set_password("TestPass123!")

            assert user.username == "testuser"
            assert user.password_hash is not None
            assert user.password_hash != "TestPass123!"

    @pytest.mark.models
    def test_password_hashing(self, app):
        """Test password hashing and verification."""
        with app.app_context():
            user = User(username="testuser")
            user.set_password("TestPass123!")

            assert user.check_password("TestPass123!")
            assert not user.check_password("wrongpassword")

    @pytest.mark.models
    def test_user_repr(self, app):
        """Test user string representation."""
        with app.app_context():
            user = User(username="testuser")
            assert repr(user) == "<User testuser>"

    @pytest.mark.models
    def test_user_relationships(self, app, user):
        """Test user relationships with transactions and goals."""
        with app.app_context():
            # Test transactions relationship
            transaction = Transaction(
                type="expense",
                category="food",
                amount=Decimal("50.00"),
                description="Test transaction",
                user_id=user.id,
            )
            db.session.add(transaction)

            # Test goals relationship
            goal = Goal(
                name="Test Goal",
                target_amount=Decimal("1000.00"),
                deadline=date.today() + timedelta(days=30),
                user_id=user.id,
            )
            db.session.add(goal)
            db.session.commit()

            assert len(user.transactions) == 1
            assert len(user.goals) == 1
            assert user.transactions[0].description == "Test transaction"
            assert user.goals[0].name == "Test Goal"


class TestTransaction:
    """Test Transaction model."""

    @pytest.mark.models
    def test_transaction_creation(self, app, user):
        """Test transaction creation."""
        with app.app_context():
            transaction = Transaction(
                type="expense",
                category="food",
                amount=Decimal("25.50"),
                description="Grocery shopping",
                notes="Weekly groceries",
                user_id=user.id,
            )
            db.session.add(transaction)
            db.session.commit()

            assert transaction.type == "expense"
            assert transaction.category == "food"
            assert transaction.amount == Decimal("25.50")
            assert transaction.description == "Grocery shopping"
            assert transaction.notes == "Weekly groceries"
            assert transaction.user_id == user.id
            assert transaction.created_at is not None
            assert transaction.date is not None

    @pytest.mark.models
    def test_transaction_repr(self, app, user):
        """Test transaction string representation."""
        with app.app_context():
            transaction = Transaction(
                type="income",
                category="salary",
                amount=Decimal("3000.00"),
                description="Monthly salary",
                user_id=user.id,
            )
            db.session.add(transaction)
            db.session.commit()

            expected = f"<Transaction {transaction.id}: income ${transaction.amount}>"
            assert repr(transaction) == expected

    @pytest.mark.models
    def test_transaction_validation(self, app, user):
        """Test transaction validation."""
        with app.app_context():
            # Test valid transaction
            transaction = Transaction(
                type="expense",
                category="food",
                amount=Decimal("25.50"),
                description="Test transaction",
                user_id=user.id,
            )
            db.session.add(transaction)
            db.session.commit()

            assert transaction.id is not None

    @pytest.mark.models
    def test_transaction_user_relationship(self, app, user):
        """Test transaction-user relationship."""
        with app.app_context():
            transaction = Transaction(
                type="expense",
                category="food",
                amount=Decimal("25.50"),
                description="Test transaction",
                user_id=user.id,
            )
            db.session.add(transaction)
            db.session.commit()

            assert transaction.user == user
            assert transaction in user.transactions

    @pytest.mark.models
    def test_transaction_decimal_precision(self, app, user):
        """Test transaction amount decimal precision."""
        with app.app_context():
            transaction = Transaction(
                type="expense",
                category="food",
                amount=Decimal("25.99"),
                description="Precise amount test",
                user_id=user.id,
            )
            db.session.add(transaction)
            db.session.commit()

            # Retrieve from database and check precision is maintained
            retrieved = Transaction.query.get(transaction.id)
            assert retrieved.amount == Decimal("25.99")
            assert str(retrieved.amount) == "25.99"


class TestGoal:
    """Test Goal model."""

    @pytest.mark.models
    def test_goal_creation(self, app, user):
        """Test goal creation."""
        with app.app_context():
            deadline = date.today() + timedelta(days=365)
            goal = Goal(
                name="Emergency Fund",
                description="Build emergency savings",
                target_amount=Decimal("10000.00"),
                current_amount=Decimal("2500.00"),
                deadline=deadline,
                status="active",
                user_id=user.id,
            )
            db.session.add(goal)
            db.session.commit()

            assert goal.name == "Emergency Fund"
            assert goal.description == "Build emergency savings"
            assert goal.target_amount == Decimal("10000.00")
            assert goal.current_amount == Decimal("2500.00")
            assert goal.deadline == deadline
            assert goal.status == "active"
            assert goal.user_id == user.id
            assert goal.created_at is not None

    @pytest.mark.models
    def test_goal_progress_percentage(self, app, user):
        """Test goal progress percentage calculation."""
        with app.app_context():
            goal = Goal(
                name="Test Goal",
                target_amount=Decimal("1000.00"),
                current_amount=Decimal("250.00"),
                deadline=date.today() + timedelta(days=30),
                user_id=user.id,
            )
            db.session.add(goal)
            db.session.commit()

            assert goal.progress_percentage == 25.0

    @pytest.mark.models
    def test_goal_is_completed(self, app, user):
        """Test goal completion detection."""
        with app.app_context():
            # Goal not completed
            goal = Goal(
                name="Test Goal",
                target_amount=Decimal("1000.00"),
                current_amount=Decimal("500.00"),
                deadline=date.today() + timedelta(days=30),
                user_id=user.id,
            )
            db.session.add(goal)
            db.session.commit()

            assert not goal.is_completed

            # Complete the goal
            goal.current_amount = Decimal("1000.00")
            db.session.commit()

            assert goal.is_completed

    @pytest.mark.models
    def test_goal_is_overdue(self, app, user):
        """Test goal overdue detection."""
        with app.app_context():
            # Future deadline - not overdue
            future_goal = Goal(
                name="Future Goal",
                target_amount=Decimal("1000.00"),
                deadline=date.today() + timedelta(days=30),
                user_id=user.id,
            )
            db.session.add(future_goal)

            # Past deadline - overdue
            overdue_goal = Goal(
                name="Overdue Goal",
                target_amount=Decimal("1000.00"),
                deadline=date.today() - timedelta(days=1),
                user_id=user.id,
            )
            db.session.add(overdue_goal)
            db.session.commit()

            assert not future_goal.is_overdue
            assert overdue_goal.is_overdue

    @pytest.mark.models
    def test_goal_add_progress(self, app, user):
        """Test adding progress to a goal."""
        with app.app_context():
            goal = Goal(
                name="Test Goal",
                target_amount=Decimal("1000.00"),
                current_amount=Decimal("200.00"),
                deadline=date.today() + timedelta(days=30),
                user_id=user.id,
            )
            db.session.add(goal)
            db.session.commit()

            # Add progress
            goal.add_progress(Decimal("300.00"))
            db.session.commit()

            assert goal.current_amount == Decimal("500.00")
            assert goal.progress_percentage == 50.0

    @pytest.mark.models
    def test_goal_update_progress(self, app, user):
        """Test updating goal progress."""
        with app.app_context():
            goal = Goal(
                name="Test Goal",
                target_amount=Decimal("1000.00"),
                current_amount=Decimal("200.00"),
                deadline=date.today() + timedelta(days=30),
                user_id=user.id,
            )
            db.session.add(goal)
            db.session.commit()

            # Update progress
            goal.update_progress(Decimal("750.00"))
            db.session.commit()

            assert goal.current_amount == Decimal("750.00")
            assert goal.progress_percentage == 75.0

    @pytest.mark.models
    def test_goal_repr(self, app, user):
        """Test goal string representation."""
        with app.app_context():
            goal = Goal(
                name="Test Goal",
                target_amount=Decimal("1000.00"),
                deadline=date.today() + timedelta(days=30),
                user_id=user.id,
            )
            db.session.add(goal)
            db.session.commit()

            expected = f"<Goal {goal.id}: Test Goal (${goal.target_amount})>"
            assert repr(goal) == expected

    @pytest.mark.models
    def test_goal_user_relationship(self, app, user):
        """Test goal-user relationship."""
        with app.app_context():
            goal = Goal(
                name="Test Goal",
                target_amount=Decimal("1000.00"),
                deadline=date.today() + timedelta(days=30),
                user_id=user.id,
            )
            db.session.add(goal)
            db.session.commit()

            assert goal.user == user
            assert goal in user.goals

    @pytest.mark.models
    def test_goal_progress_boundary_conditions(self, app, user):
        """Test goal progress boundary conditions."""
        with app.app_context():
            goal = Goal(
                name="Test Goal",
                target_amount=Decimal("1000.00"),
                current_amount=Decimal("0.00"),
                deadline=date.today() + timedelta(days=30),
                user_id=user.id,
            )
            db.session.add(goal)
            db.session.commit()

            # Test 0% progress
            assert goal.progress_percentage == 0.0
            assert not goal.is_completed

            # Test 100% progress
            goal.current_amount = Decimal("1000.00")
            assert goal.progress_percentage == 100.0
            assert goal.is_completed

            # Test over 100% progress
            goal.current_amount = Decimal("1200.00")
            assert goal.progress_percentage == 120.0
            assert goal.is_completed

    @pytest.mark.models
    def test_goal_decimal_precision(self, app, user):
        """Test goal amount decimal precision."""
        with app.app_context():
            goal = Goal(
                name="Precision Test",
                target_amount=Decimal("1234.56"),
                current_amount=Decimal("123.45"),
                deadline=date.today() + timedelta(days=30),
                user_id=user.id,
            )
            db.session.add(goal)
            db.session.commit()

            # Retrieve from database and check precision is maintained
            retrieved = Goal.query.get(goal.id)
            assert retrieved.target_amount == Decimal("1234.56")
            assert retrieved.current_amount == Decimal("123.45")
            assert str(retrieved.target_amount) == "1234.56"
            assert str(retrieved.current_amount) == "123.45"
