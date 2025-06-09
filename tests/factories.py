"""Factory classes for test data generation."""

from datetime import date, timedelta
from decimal import Decimal

import factory
from factory.alchemy import SQLAlchemyModelFactory
from werkzeug.security import generate_password_hash

from app import db
from app.models.goal import Goal
from app.models.transaction import Transaction
from app.models.user import User


class UserFactory(SQLAlchemyModelFactory):
    """Factory for User model."""

    class Meta:
        model = User
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    username = factory.Sequence(lambda n: f"user{n}")
    password_hash = factory.LazyFunction(lambda: generate_password_hash("TestPass123!"))


class TransactionFactory(SQLAlchemyModelFactory):
    """Factory for Transaction model."""

    class Meta:
        model = Transaction
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    type = factory.Faker("random_element", elements=("income", "expense"))
    category = factory.LazyAttribute(
        lambda obj: factory.Faker(
            "random_element",
            elements=(
                ["salary", "freelance", "investment"]
                if obj.type == "income"
                else [
                    "food",
                    "transportation",
                    "entertainment",
                    "utilities",
                    "healthcare",
                ]
            ),
        ).generate()
    )
    amount = factory.Faker("pydecimal", left_digits=4, right_digits=2, positive=True)
    description = factory.Faker("sentence", nb_words=4)
    notes = factory.Faker("text", max_nb_chars=200)
    date = factory.Faker("date_between", start_date="-1y", end_date="today")
    user = factory.SubFactory(UserFactory)


class GoalFactory(SQLAlchemyModelFactory):
    """Factory for Goal model."""

    class Meta:
        model = Goal
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    name = factory.Faker("catch_phrase")
    description = factory.Faker("paragraph", nb_sentences=3)
    target_amount = factory.Faker(
        "pydecimal", left_digits=5, right_digits=2, positive=True
    )
    current_amount = factory.LazyAttribute(
        lambda obj: Decimal(str(float(obj.target_amount) * 0.3))
    )
    deadline = factory.Faker("date_between", start_date="+30d", end_date="+2y")
    status = factory.Faker("random_element", elements=("active", "paused", "completed"))
    user = factory.SubFactory(UserFactory)


# Specialized factories for specific test scenarios
class ExpenseTransactionFactory(TransactionFactory):
    """Factory for expense transactions."""

    type = "expense"
    category = factory.Faker(
        "random_element",
        elements=["food", "transportation", "entertainment", "utilities", "healthcare"],
    )


class IncomeTransactionFactory(TransactionFactory):
    """Factory for income transactions."""

    type = "income"
    category = factory.Faker(
        "random_element", elements=["salary", "freelance", "investment", "bonus"]
    )


class ActiveGoalFactory(GoalFactory):
    """Factory for active goals."""

    status = "active"
    deadline = factory.Faker("date_between", start_date="+30d", end_date="+1y")


class CompletedGoalFactory(GoalFactory):
    """Factory for completed goals."""

    status = "completed"
    current_amount = factory.SelfAttribute("target_amount")


class UserWithDataFactory(UserFactory):
    """Factory for user with associated transactions and goals."""

    @factory.post_generation
    def transactions(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for transaction in extracted:
                transaction.user = self
        else:
            # Create default transactions
            ExpenseTransactionFactory.create_batch(3, user=self)
            IncomeTransactionFactory.create_batch(2, user=self)

    @factory.post_generation
    def goals(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for goal in extracted:
                goal.user = self
        else:
            # Create default goals
            ActiveGoalFactory.create_batch(2, user=self)
            CompletedGoalFactory.create(user=self)
