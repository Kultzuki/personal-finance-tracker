"""Integration tests for end-to-end workflows."""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from app import db
from app.models.goal import Goal
from app.models.transaction import Transaction
from app.models.user import User


class TestUserWorkflow:
    """Test complete user workflows."""

    @pytest.mark.integration
    def test_complete_user_registration_and_login_flow(self, client):
        """Test complete user registration and login workflow."""
        # Register a new user
        response = client.post(
            "/auth/register",
            data={
                "username": "newuser",
                "password": "NewPass123!",
                "password2": "NewPass123!",
            },
        )
        assert response.status_code == 302  # Redirect to dashboard

        # Verify user was created
        user = User.query.filter_by(username="newuser").first()
        assert user is not None

        # Logout
        response = client.get("/auth/logout")
        assert response.status_code == 302

        # Login with the new user
        response = client.post(
            "/auth/login", data={"username": "newuser", "password": "NewPass123!"}
        )
        assert response.status_code == 302  # Redirect to dashboard

        # Access dashboard
        response = client.get("/")
        assert response.status_code == 200
        assert b"Dashboard" in response.data

    @pytest.mark.integration
    def test_transaction_management_workflow(self, logged_in_user):
        """Test complete transaction management workflow."""
        # Create a new transaction
        response = logged_in_user.post(
            "/transactions/create",
            data={
                "type": "expense",
                "description": "Grocery Shopping",
                "amount": "125.50",
                "category": "food",
                "date": date.today().strftime("%Y-%m-%d"),
                "notes": "Weekly grocery run",
            },
        )
        assert response.status_code == 302

        # Verify transaction was created
        transaction = Transaction.query.filter_by(
            description="Grocery Shopping"
        ).first()
        assert transaction is not None
        assert transaction.amount == Decimal("125.50")

        # View transaction list
        response = logged_in_user.get("/transactions/")
        assert response.status_code == 200
        assert b"Grocery Shopping" in response.data

        # Edit the transaction
        response = logged_in_user.post(
            f"/transactions/{transaction.id}/edit",
            data={
                "type": "expense",
                "description": "Updated Grocery Shopping",
                "amount": "150.00",
                "category": "food",
                "date": date.today().strftime("%Y-%m-%d"),
                "notes": "Updated notes",
            },
        )
        assert response.status_code == 302

        # Verify transaction was updated
        updated_transaction = Transaction.query.get(transaction.id)
        assert updated_transaction.description == "Updated Grocery Shopping"
        assert updated_transaction.amount == Decimal("150.00")

        # Delete the transaction
        response = logged_in_user.post(f"/transactions/{transaction.id}/delete")
        assert response.status_code == 302

        # Verify transaction was deleted
        deleted_transaction = Transaction.query.get(transaction.id)
        assert deleted_transaction is None

    @pytest.mark.integration
    def test_goal_management_workflow(self, logged_in_user):
        """Test complete goal management workflow."""
        future_date = (date.today() + timedelta(days=365)).strftime("%Y-%m-%d")

        # Create a new goal
        response = logged_in_user.post(
            "/goals/create",
            data={
                "name": "Emergency Fund",
                "description": "Build emergency savings",
                "target_amount": "10000.00",
                "current_amount": "2000.00",
                "deadline": future_date,
                "status": "active",
            },
        )
        assert response.status_code == 302

        # Verify goal was created
        goal = Goal.query.filter_by(name="Emergency Fund").first()
        assert goal is not None
        assert goal.target_amount == Decimal("10000.00")
        assert goal.current_amount == Decimal("2000.00")

        # View goal list
        response = logged_in_user.get("/goals/")
        assert response.status_code == 200
        assert b"Emergency Fund" in response.data

        # Update goal progress
        response = logged_in_user.post(
            f"/goals/{goal.id}/update-progress", data={"amount": "500.00"}
        )
        assert response.status_code == 302

        # Verify progress was updated
        updated_goal = Goal.query.get(goal.id)
        assert updated_goal.current_amount == Decimal("2500.00")

        # Set specific progress
        response = logged_in_user.post(
            f"/goals/{goal.id}/set-progress", data={"current_amount": "7500.00"}
        )
        assert response.status_code == 302

        # Verify progress was set
        updated_goal = Goal.query.get(goal.id)
        assert updated_goal.current_amount == Decimal("7500.00")

        # Complete the goal
        response = logged_in_user.post(f"/goals/{goal.id}/complete")
        assert response.status_code == 302

        # Verify goal was completed
        completed_goal = Goal.query.get(goal.id)
        assert completed_goal.status == "completed"
        assert completed_goal.current_amount == completed_goal.target_amount


class TestDataConsistency:
    """Test data consistency across operations."""

    @pytest.mark.integration
    def test_user_data_isolation(self, app, client, auth):
        """Test that user data is properly isolated."""
        with app.app_context():
            # Create two users with data
            user1 = User(username="user1")
            user1.set_password("TestPass123!")
            user2 = User(username="user2")
            user2.set_password("TestPass123!")

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

            db.session.add_all([trans1, trans2, goal1, goal2])
            db.session.commit()

            # Test user1 can only see their data
            response = client.post(
                "/auth/login", data={"username": "user1", "password": "TestPass123!"}
            )
            assert response.status_code == 302

            # Check transactions
            response = client.get("/transactions/")
            assert b"User1 Transaction" in response.data
            assert b"User2 Transaction" not in response.data

            # Check goals
            response = client.get("/goals/")
            assert b"User1 Goal" in response.data
            assert b"User2 Goal" not in response.data

            # Test user1 cannot access user2's data directly
            response = client.get(f"/transactions/{trans2.id}/edit")
            assert response.status_code == 404

            response = client.get(f"/goals/{goal2.id}/edit")
            assert response.status_code == 404

    @pytest.mark.integration
    def test_database_transaction_rollback(self, app, logged_in_user):
        """Test database transaction rollback on errors."""
        with app.app_context():
            initial_count = Transaction.query.count()

            # Attempt to create invalid transaction (this should fail)
            try:
                response = logged_in_user.post(
                    "/transactions/create",
                    data={
                        "type": "invalid_type",  # Invalid type
                        "description": "Test Transaction",
                        "amount": "150.00",
                        "category": "food",
                        "date": date.today().strftime("%Y-%m-%d"),
                    },
                )
                # The form should catch this, but if it somehow passes,
                # database constraints should prevent it
            except Exception:
                pass

            # Verify no new transactions were created
            final_count = Transaction.query.count()
            assert final_count == initial_count


class TestFormValidationIntegration:
    """Test form validation in real workflows."""

    @pytest.mark.integration
    def test_transaction_form_validation_workflow(self, logged_in_user):
        """Test transaction form validation in complete workflow."""
        # Test invalid amount
        response = logged_in_user.post(
            "/transactions/create",
            data={
                "type": "expense",
                "description": "Test Transaction",
                "amount": "0.00",  # Invalid amount
                "category": "food",
                "date": date.today().strftime("%Y-%m-%d"),
            },
        )
        assert response.status_code == 200  # Should stay on form
        assert b"Amount must be between" in response.data

        # Test invalid date (future)
        future_date = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        response = logged_in_user.post(
            "/transactions/create",
            data={
                "type": "expense",
                "description": "Test Transaction",
                "amount": "150.00",
                "category": "food",
                "date": future_date,  # Invalid future date
            },
        )
        assert response.status_code == 200
        assert b"cannot be in the future" in response.data

        # Test valid transaction
        response = logged_in_user.post(
            "/transactions/create",
            data={
                "type": "expense",
                "description": "Valid Transaction",
                "amount": "150.00",
                "category": "food",
                "date": date.today().strftime("%Y-%m-%d"),
            },
        )
        assert response.status_code == 302  # Should redirect on success

        # Verify transaction was created
        transaction = Transaction.query.filter_by(
            description="Valid Transaction"
        ).first()
        assert transaction is not None

    @pytest.mark.integration
    def test_goal_form_validation_workflow(self, logged_in_user):
        """Test goal form validation in complete workflow."""
        # Test invalid deadline (past date)
        past_date = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        response = logged_in_user.post(
            "/goals/create",
            data={
                "name": "Test Goal",
                "target_amount": "1000.00",
                "deadline": past_date,  # Invalid past date
                "status": "active",
            },
        )
        assert response.status_code == 200
        assert b"must be in the future" in response.data

        # Test current amount exceeding target
        future_date = (date.today() + timedelta(days=30)).strftime("%Y-%m-%d")
        response = logged_in_user.post(
            "/goals/create",
            data={
                "name": "Test Goal",
                "target_amount": "1000.00",
                "current_amount": "1500.00",  # Exceeds target
                "deadline": future_date,
                "status": "active",
            },
        )
        assert response.status_code == 200
        assert b"cannot exceed the target amount" in response.data

        # Test valid goal
        response = logged_in_user.post(
            "/goals/create",
            data={
                "name": "Valid Goal",
                "target_amount": "1000.00",
                "current_amount": "250.00",
                "deadline": future_date,
                "status": "active",
            },
        )
        assert response.status_code == 302  # Should redirect on success

        # Verify goal was created
        goal = Goal.query.filter_by(name="Valid Goal").first()
        assert goal is not None


class TestAPIEndpoints:
    """Test API endpoints integration."""

    @pytest.mark.integration
    def test_categories_api_integration(self, logged_in_user):
        """Test categories API with real data."""
        # Test expense categories
        response = logged_in_user.get("/transactions/api/categories/expense")
        assert response.status_code == 200
        assert response.is_json

        categories = response.get_json()
        assert isinstance(categories, list)
        assert len(categories) > 0
        assert any("food" in cat for cat in categories)

        # Test income categories
        response = logged_in_user.get("/transactions/api/categories/income")
        assert response.status_code == 200
        assert response.is_json

        categories = response.get_json()
        assert isinstance(categories, list)
        assert any("salary" in cat for cat in categories)

    @pytest.mark.integration
    def test_goal_stats_api_integration(self, logged_in_user, multiple_goals):
        """Test goal stats API with real data."""
        response = logged_in_user.get("/goals/api/stats")
        assert response.status_code == 200
        assert response.is_json

        stats = response.get_json()
        assert "total_goals" in stats
        assert "active_goals" in stats
        assert "completed_goals" in stats
        assert stats["total_goals"] == len(multiple_goals)


class TestPerformance:
    """Test performance with larger datasets."""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_transaction_list_performance(self, app, logged_in_user, user):
        """Test transaction list performance with many transactions."""
        with app.app_context():
            # Create many transactions
            transactions = []
            for i in range(100):
                transaction = Transaction(
                    type="expense" if i % 2 == 0 else "income",
                    category="food" if i % 2 == 0 else "salary",
                    amount=Decimal(f"{100 + i}.00"),
                    description=f"Test Transaction {i}",
                    user_id=user.id,
                )
                transactions.append(transaction)

            db.session.add_all(transactions)
            db.session.commit()

            # Test that page loads in reasonable time
            import time

            start_time = time.time()

            response = logged_in_user.get("/transactions/")

            end_time = time.time()
            assert response.status_code == 200
            assert (end_time - start_time) < 2.0  # Should load in less than 2 seconds
