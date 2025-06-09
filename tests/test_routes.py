"""Tests for application routes."""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from flask import url_for

from app import db
from app.models.goal import Goal
from app.models.transaction import Transaction
from app.models.user import User


class TestAuthRoutes:
    """Test authentication routes."""

    @pytest.mark.routes
    def test_register_get(self, client):
        """Test GET request to register page."""
        response = client.get("/auth/register")
        assert response.status_code == 200
        assert b"Create Account" in response.data

    @pytest.mark.routes
    def test_register_post_valid(self, client):
        """Test valid registration."""
        response = client.post(
            "/auth/register",
            data={
                "username": "testuser",
                "password": "TestPass123!",
                "password2": "TestPass123!",
            },
        )

        assert response.status_code == 302  # Redirect after successful registration

        # Check user was created
        user = User.query.filter_by(username="testuser").first()
        assert user is not None

    @pytest.mark.routes
    def test_register_post_invalid(self, client):
        """Test invalid registration."""
        response = client.post(
            "/auth/register",
            data={
                "username": "ab",  # Too short
                "password": "weak",  # Too weak
                "password2": "different",  # Doesn't match
            },
        )

        assert response.status_code == 200
        assert b"Please correct the errors below" in response.data

    @pytest.mark.routes
    def test_login_get(self, client):
        """Test GET request to login page."""
        response = client.get("/auth/login")
        assert response.status_code == 200
        assert b"Sign In" in response.data

    @pytest.mark.routes
    def test_login_post_valid(self, client, user):
        """Test valid login."""
        response = client.post(
            "/auth/login", data={"username": "testuser", "password": "TestPass123!"}
        )

        assert response.status_code == 302  # Redirect after successful login

    @pytest.mark.routes
    def test_login_post_invalid(self, client, user):
        """Test invalid login."""
        response = client.post(
            "/auth/login", data={"username": "testuser", "password": "wrongpassword"}
        )

        assert response.status_code == 200
        assert b"Invalid username or password" in response.data

    @pytest.mark.routes
    def test_logout(self, logged_in_user):
        """Test logout."""
        response = logged_in_user.get("/auth/logout")
        assert response.status_code == 302  # Redirect after logout

    @pytest.mark.routes
    def test_login_required_redirect(self, client):
        """Test that protected routes redirect to login."""
        response = client.get("/transactions/")
        assert response.status_code == 302
        assert "/auth/login" in response.location


class TestMainRoutes:
    """Test main application routes."""

    @pytest.mark.routes
    def test_index_anonymous(self, client):
        """Test index page for anonymous users."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"Welcome to Personal Finance Tracker" in response.data

    @pytest.mark.routes
    def test_index_logged_in(self, logged_in_user):
        """Test dashboard for logged-in users."""
        response = logged_in_user.get("/")
        assert response.status_code == 200
        assert b"Dashboard" in response.data


class TestTransactionRoutes:
    """Test transaction routes."""

    @pytest.mark.routes
    def test_transaction_index(self, logged_in_user):
        """Test transaction list page."""
        response = logged_in_user.get("/transactions/")
        assert response.status_code == 200
        assert b"Transactions" in response.data

    @pytest.mark.routes
    def test_transaction_create_get(self, logged_in_user):
        """Test GET request to create transaction page."""
        response = logged_in_user.get("/transactions/create")
        assert response.status_code == 200
        assert b"Save Transaction" in response.data

    @pytest.mark.routes
    def test_transaction_create_post_valid(self, logged_in_user):
        """Test valid transaction creation."""
        response = logged_in_user.post(
            "/transactions/create",
            data={
                "type": "expense",
                "description": "Test Transaction",
                "amount": "150.75",
                "category": "food",
                "date": date.today().strftime("%Y-%m-%d"),
                "notes": "Test notes",
            },
        )

        assert response.status_code == 302  # Redirect after successful creation

        # Check transaction was created
        transaction = Transaction.query.filter_by(
            description="Test Transaction"
        ).first()
        assert transaction is not None
        assert transaction.amount == Decimal("150.75")

    @pytest.mark.routes
    def test_transaction_create_post_invalid(self, logged_in_user):
        """Test invalid transaction creation."""
        response = logged_in_user.post(
            "/transactions/create",
            data={
                "type": "",  # Missing type
                "description": "",  # Missing description
                "amount": "0",  # Invalid amount
                "category": "",  # Missing category
                "date": "",  # Missing date
            },
        )

        assert response.status_code == 200
        assert b"Please correct the errors below" in response.data

    @pytest.mark.routes
    def test_transaction_edit_get(self, logged_in_user, transaction):
        """Test GET request to edit transaction page."""
        response = logged_in_user.get(f"/transactions/{transaction.id}/edit")
        assert response.status_code == 200
        assert b"Save Transaction" in response.data

    @pytest.mark.routes
    def test_transaction_edit_post_valid(self, logged_in_user, transaction):
        """Test valid transaction edit."""
        response = logged_in_user.post(
            f"/transactions/{transaction.id}/edit",
            data={
                "type": "expense",
                "description": "Updated Transaction",
                "amount": "200.00",
                "category": "food",
                "date": date.today().strftime("%Y-%m-%d"),
                "notes": "Updated notes",
            },
        )

        assert response.status_code == 302  # Redirect after successful update

        # Check transaction was updated
        updated_transaction = Transaction.query.get(transaction.id)
        assert updated_transaction.description == "Updated Transaction"
        assert updated_transaction.amount == Decimal("200.00")

    @pytest.mark.routes
    def test_transaction_delete_get(self, logged_in_user, transaction):
        """Test GET request to delete transaction page."""
        response = logged_in_user.get(f"/transactions/{transaction.id}/delete")
        assert response.status_code == 200
        assert b"Delete Transaction" in response.data

    @pytest.mark.routes
    def test_transaction_delete_post(self, logged_in_user, transaction):
        """Test transaction deletion."""
        transaction_id = transaction.id

        response = logged_in_user.post(f"/transactions/{transaction_id}/delete")
        assert response.status_code == 302  # Redirect after deletion

        # Check transaction was deleted
        deleted_transaction = Transaction.query.get(transaction_id)
        assert deleted_transaction is None

    @pytest.mark.routes
    def test_transaction_filter(self, logged_in_user, multiple_transactions):
        """Test transaction filtering."""
        response = logged_in_user.get("/transactions/?type=income")
        assert response.status_code == 200

        response = logged_in_user.get("/transactions/?category=food")
        assert response.status_code == 200

    @pytest.mark.routes
    def test_categories_api(self, logged_in_user):
        """Test categories API endpoint."""
        response = logged_in_user.get("/transactions/api/categories/expense")
        assert response.status_code == 200
        assert response.is_json

        json_data = response.get_json()
        assert isinstance(json_data, list)
        assert len(json_data) > 0


class TestGoalRoutes:
    """Test goal routes."""

    @pytest.mark.routes
    def test_goal_index(self, logged_in_user):
        """Test goal list page."""
        response = logged_in_user.get("/goals/")
        assert response.status_code == 200
        assert b"Goals" in response.data

    @pytest.mark.routes
    def test_goal_create_get(self, logged_in_user):
        """Test GET request to create goal page."""
        response = logged_in_user.get("/goals/create")
        assert response.status_code == 200
        assert b"Save Goal" in response.data

    @pytest.mark.routes
    def test_goal_create_post_valid(self, logged_in_user):
        """Test valid goal creation."""
        future_date = (date.today() + timedelta(days=180)).strftime("%Y-%m-%d")

        response = logged_in_user.post(
            "/goals/create",
            data={
                "name": "Test Goal",
                "description": "Test goal description",
                "target_amount": "5000.00",
                "current_amount": "1000.00",
                "deadline": future_date,
                "status": "active",
            },
        )

        assert response.status_code == 302  # Redirect after successful creation

        # Check goal was created
        goal = Goal.query.filter_by(name="Test Goal").first()
        assert goal is not None
        assert goal.target_amount == Decimal("5000.00")

    @pytest.mark.routes
    def test_goal_create_post_invalid(self, logged_in_user):
        """Test invalid goal creation."""
        response = logged_in_user.post(
            "/goals/create",
            data={
                "name": "",  # Missing name
                "target_amount": "0",  # Invalid amount
                "deadline": "",  # Missing deadline
                "status": "",  # Missing status
            },
        )

        assert response.status_code == 200
        assert b"Please correct the errors below" in response.data

    @pytest.mark.routes
    def test_goal_edit_get(self, logged_in_user, goal):
        """Test GET request to edit goal page."""
        response = logged_in_user.get(f"/goals/{goal.id}/edit")
        assert response.status_code == 200
        assert b"Save Goal" in response.data

    @pytest.mark.routes
    def test_goal_edit_post_valid(self, logged_in_user, goal):
        """Test valid goal edit."""
        future_date = (date.today() + timedelta(days=300)).strftime("%Y-%m-%d")

        response = logged_in_user.post(
            f"/goals/{goal.id}/edit",
            data={
                "name": "Updated Goal",
                "description": "Updated description",
                "target_amount": "15000.00",
                "current_amount": "5000.00",
                "deadline": future_date,
                "status": "active",
            },
        )

        assert response.status_code == 302  # Redirect after successful update

        # Check goal was updated
        updated_goal = Goal.query.get(goal.id)
        assert updated_goal.name == "Updated Goal"
        assert updated_goal.target_amount == Decimal("15000.00")

    @pytest.mark.routes
    def test_goal_update_progress(self, logged_in_user, goal):
        """Test updating goal progress."""
        response = logged_in_user.post(
            f"/goals/{goal.id}/update-progress", data={"amount": "500.00"}
        )

        assert response.status_code == 302  # Redirect after update

        # Check progress was updated
        updated_goal = Goal.query.get(goal.id)
        assert updated_goal.current_amount == Decimal("3000.00")  # 2500 + 500

    @pytest.mark.routes
    def test_goal_set_progress(self, logged_in_user, goal):
        """Test setting goal progress."""
        response = logged_in_user.post(
            f"/goals/{goal.id}/set-progress", data={"current_amount": "7500.00"}
        )

        assert response.status_code == 302  # Redirect after update

        # Check progress was set
        updated_goal = Goal.query.get(goal.id)
        assert updated_goal.current_amount == Decimal("7500.00")

    @pytest.mark.routes
    def test_goal_complete(self, logged_in_user, goal):
        """Test marking goal as complete."""
        response = logged_in_user.post(f"/goals/{goal.id}/complete")
        assert response.status_code == 302  # Redirect after completion

        # Check goal was marked as completed
        completed_goal = Goal.query.get(goal.id)
        assert completed_goal.status == "completed"
        assert completed_goal.current_amount == completed_goal.target_amount

    @pytest.mark.routes
    def test_goal_delete_get(self, logged_in_user, goal):
        """Test GET request to delete goal page."""
        response = logged_in_user.get(f"/goals/{goal.id}/delete")
        assert response.status_code == 200
        assert b"Delete Goal" in response.data

    @pytest.mark.routes
    def test_goal_delete_post(self, logged_in_user, goal):
        """Test goal deletion."""
        goal_id = goal.id

        response = logged_in_user.post(f"/goals/{goal_id}/delete")
        assert response.status_code == 302  # Redirect after deletion

        # Check goal was deleted
        deleted_goal = Goal.query.get(goal_id)
        assert deleted_goal is None

    @pytest.mark.routes
    def test_goal_stats_api(self, logged_in_user, multiple_goals):
        """Test goal stats API endpoint."""
        response = logged_in_user.get("/goals/api/stats")
        assert response.status_code == 200
        assert response.is_json

        json_data = response.get_json()
        assert "total_goals" in json_data
        assert "active_goals" in json_data
        assert "completed_goals" in json_data


class TestUserIsolation:
    """Test user data isolation."""

    @pytest.mark.routes
    def test_transaction_isolation(self, app, client, auth):
        """Test that users can only see their own transactions."""
        with app.app_context():
            # Create two users
            user1 = User(username="user1", password_hash="hash1")
            user2 = User(username="user2", password_hash="hash2")
            db.session.add_all([user1, user2])
            db.session.commit()

            # Create transactions for each user
            trans1 = Transaction(
                type="expense",
                category="food",
                amount=Decimal("50.00"),
                description="User1 Transaction",
                user_id=user1.id,
            )
            trans2 = Transaction(
                type="expense",
                category="food",
                amount=Decimal("75.00"),
                description="User2 Transaction",
                user_id=user2.id,
            )
            db.session.add_all([trans1, trans2])
            db.session.commit()

            # Login as user1 and check transactions
            auth.register("user1", "TestPass123!")
            auth.login("user1", "TestPass123!")

            response = client.get("/transactions/")
            assert response.status_code == 200
            assert b"User1 Transaction" in response.data
            assert b"User2 Transaction" not in response.data

    @pytest.mark.routes
    def test_goal_isolation(self, app, client, auth):
        """Test that users can only see their own goals."""
        with app.app_context():
            # Create two users
            user1 = User(username="user1", password_hash="hash1")
            user2 = User(username="user2", password_hash="hash2")
            db.session.add_all([user1, user2])
            db.session.commit()

            # Create goals for each user
            goal1 = Goal(
                name="User1 Goal",
                target_amount=Decimal("1000.00"),
                deadline=date.today() + timedelta(days=30),
                user_id=user1.id,
            )
            goal2 = Goal(
                name="User2 Goal",
                target_amount=Decimal("2000.00"),
                deadline=date.today() + timedelta(days=30),
                user_id=user2.id,
            )
            db.session.add_all([goal1, goal2])
            db.session.commit()

            # Login as user1 and check goals
            auth.register("user1", "TestPass123!")
            auth.login("user1", "TestPass123!")

            response = client.get("/goals/")
            assert response.status_code == 200
            assert b"User1 Goal" in response.data
            assert b"User2 Goal" not in response.data


class TestErrorHandling:
    """Test error handling."""

    @pytest.mark.routes
    def test_404_error(self, logged_in_user):
        """Test 404 error handling."""
        response = logged_in_user.get("/nonexistent-page")
        assert response.status_code == 404

    @pytest.mark.routes
    def test_transaction_not_found(self, logged_in_user):
        """Test accessing non-existent transaction."""
        response = logged_in_user.get("/transactions/99999/edit")
        assert response.status_code == 404

    @pytest.mark.routes
    def test_goal_not_found(self, logged_in_user):
        """Test accessing non-existent goal."""
        response = logged_in_user.get("/goals/99999/edit")
        assert response.status_code == 404
