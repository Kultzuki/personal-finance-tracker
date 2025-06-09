"""Test configuration and fixtures."""

import os
import tempfile
from decimal import Decimal

import pytest
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models.goal import Goal
from app.models.transaction import Transaction
from app.models.user import User


@pytest.fixture
def app():
    """Create and configure a test application."""
    # Create a temporary file for the test database
    db_fd, db_path = tempfile.mkstemp()

    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
            "WTF_CSRF_ENABLED": False,  # Disable CSRF for testing
            "SECRET_KEY": "test-secret-key",
        }
    )

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture
def auth(client):
    """Authentication helper."""

    class AuthActions:
        def __init__(self, client):
            self._client = client

        def login(self, username="testuser", password="TestPass123!"):
            return self._client.post(
                "/auth/login", data={"username": username, "password": password}
            )

        def logout(self):
            return self._client.get("/auth/logout")

        def register(
            self, username="testuser", password="TestPass123!", password2=None
        ):
            if password2 is None:
                password2 = password
            return self._client.post(
                "/auth/register",
                data={
                    "username": username,
                    "password": password,
                    "password2": password2,
                },
            )

    return AuthActions(client)


@pytest.fixture
def user(app):
    """Create a test user."""
    with app.app_context():
        user = User(
            username="testuser", password_hash=generate_password_hash("TestPass123!")
        )
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def transaction(app, user):
    """Create a test transaction."""
    with app.app_context():
        transaction = Transaction(
            type="expense",
            category="food",
            amount=Decimal("25.50"),
            description="Test grocery shopping",
            notes="Test notes",
            user_id=user.id,
        )
        db.session.add(transaction)
        db.session.commit()
        return transaction


@pytest.fixture
def goal(app, user):
    """Create a test goal."""
    with app.app_context():
        from datetime import date, timedelta

        goal = Goal(
            name="Test Emergency Fund",
            description="Test goal description",
            target_amount=Decimal("10000.00"),
            current_amount=Decimal("2500.00"),
            deadline=date.today() + timedelta(days=365),
            status="active",
            user_id=user.id,
        )
        db.session.add(goal)
        db.session.commit()
        return goal


@pytest.fixture
def logged_in_user(client, auth, user):
    """Login a user and return the client."""
    auth.login()
    return client


# Test data fixtures
@pytest.fixture
def sample_transaction_data():
    """Sample transaction data for testing."""
    return {
        "type": "expense",
        "description": "Test Transaction",
        "amount": Decimal("150.75"),
        "category": "food",
        "notes": "Test notes",
    }


@pytest.fixture
def sample_goal_data():
    """Sample goal data for testing."""
    from datetime import date, timedelta

    return {
        "name": "Test Goal",
        "description": "Test goal description",
        "target_amount": Decimal("5000.00"),
        "current_amount": Decimal("1000.00"),
        "deadline": date.today() + timedelta(days=180),
        "status": "active",
    }


@pytest.fixture
def multiple_transactions(app, user):
    """Create multiple test transactions."""
    with app.app_context():
        from datetime import date, timedelta

        transactions = []
        base_date = date.today()

        # Income transactions
        for i in range(3):
            t = Transaction(
                type="income",
                category="salary",
                amount=Decimal(f"{3000 + i * 100}.00"),
                description=f"Salary payment {i + 1}",
                date=base_date - timedelta(days=i * 30),
                user_id=user.id,
            )
            db.session.add(t)
            transactions.append(t)

        # Expense transactions
        categories = ["food", "transportation", "entertainment"]
        for i, category in enumerate(categories):
            t = Transaction(
                type="expense",
                category=category,
                amount=Decimal(f"{200 + i * 50}.00"),
                description=f"Test {category} expense",
                date=base_date - timedelta(days=i * 10),
                user_id=user.id,
            )
            db.session.add(t)
            transactions.append(t)

        db.session.commit()
        return transactions


@pytest.fixture
def multiple_goals(app, user):
    """Create multiple test goals."""
    with app.app_context():
        from datetime import date, timedelta

        goals = []
        base_date = date.today()

        goal_data = [
            ("Emergency Fund", 10000, 2500, "active"),
            ("Vacation", 3000, 1500, "active"),
            ("Car Down Payment", 5000, 5000, "completed"),
        ]

        for i, (name, target, current, status) in enumerate(goal_data):
            goal = Goal(
                name=name,
                description=f"Test {name.lower()} goal",
                target_amount=Decimal(str(target)),
                current_amount=Decimal(str(current)),
                deadline=base_date + timedelta(days=180 + i * 30),
                status=status,
                user_id=user.id,
            )
            db.session.add(goal)
            goals.append(goal)

        db.session.commit()
        return goals
