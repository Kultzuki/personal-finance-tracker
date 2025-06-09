"""Helper utilities for the application."""

from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Union

from flask import flash
from sqlalchemy import and_, extract, func

from app import db
from app.models.goal import Goal
from app.models.transaction import Transaction


def format_currency(amount: Decimal) -> str:
    """Format decimal amount as currency string."""
    return f"${amount:,.2f}"


def calculate_percentage(current: Decimal, target: Decimal) -> float:
    """Calculate percentage with safe division."""
    if target == 0:
        return 0.0
    return float((current / target) * 100)


def validate_decimal_precision(value: Union[str, Decimal], precision: int = 2) -> bool:
    """Validate that a decimal value has the correct precision."""
    try:
        decimal_value = Decimal(str(value))
        return decimal_value.as_tuple().exponent >= -precision
    except (ValueError, TypeError):
        return False


def safe_flash(message: str, category: str = "info") -> None:
    """Safely flash a message with emoji support."""
    try:
        flash(message, category)
    except Exception:
        # Fallback without emojis if there are encoding issues
        flash(message.encode("ascii", "ignore").decode("ascii"), category)


class FlashMessages:
    """Centralized flash message management."""

    @staticmethod
    def success(message: str) -> None:
        """Flash success message with emoji."""
        safe_flash(f"🎉 {message}", "success")

    @staticmethod
    def error(message: str) -> None:
        """Flash error message with emoji."""
        safe_flash(f"❌ {message}", "danger")

    @staticmethod
    def warning(message: str) -> None:
        """Flash warning message with emoji."""
        safe_flash(f"⚠️ {message}", "warning")

    @staticmethod
    def info(message: str) -> None:
        """Flash info message with emoji."""
        safe_flash(f"ℹ️ {message}", "info")


class TransactionHelper:
    """Helper class for transaction-related operations."""

    @staticmethod
    def get_category_choices(transaction_type: str) -> List[Tuple[str, str]]:
        """Get category choices based on transaction type."""
        income_categories = [
            ("salary", "Salary"),
            ("freelance", "Freelance"),
            ("investment", "Investment"),
            ("bonus", "Bonus"),
            ("gift", "Gift"),
            ("other_income", "Other Income"),
        ]

        expense_categories = [
            ("food", "Food & Dining"),
            ("transportation", "Transportation"),
            ("shopping", "Shopping"),
            ("entertainment", "Entertainment"),
            ("bills", "Bills & Utilities"),
            ("healthcare", "Healthcare"),
            ("education", "Education"),
            ("travel", "Travel"),
            ("other_expense", "Other Expense"),
        ]

        return income_categories if transaction_type == "income" else expense_categories

    @staticmethod
    def calculate_monthly_summary(
        user_id: int, year: int, month: int
    ) -> Dict[str, Decimal]:
        """Calculate monthly income, expenses, and net for a user."""
        base_query = Transaction.query.filter(
            and_(
                Transaction.user_id == user_id,
                extract("year", Transaction.date) == year,
                extract("month", Transaction.date) == month,
            )
        )

        income = base_query.filter(Transaction.type == "income").with_entities(
            func.sum(Transaction.amount)
        ).scalar() or Decimal("0")

        expenses = base_query.filter(Transaction.type == "expense").with_entities(
            func.sum(Transaction.amount)
        ).scalar() or Decimal("0")

        return {"income": income, "expenses": expenses, "net": income - expenses}


class GoalHelper:
    """Helper class for goal-related operations."""

    @staticmethod
    def calculate_goal_stats(user_id: int) -> Dict[str, int]:
        """Calculate goal statistics for a user."""
        base_query = Goal.query.filter(Goal.user_id == user_id)

        total_goals = base_query.count()
        active_goals = base_query.filter(Goal.status == "active").count()
        completed_goals = base_query.filter(Goal.status == "completed").count()
        paused_goals = base_query.filter(Goal.status == "paused").count()

        return {
            "total_goals": total_goals,
            "active_goals": active_goals,
            "completed_goals": completed_goals,
            "paused_goals": paused_goals,
        }

    @staticmethod
    def get_motivation_message(progress_percentage: float) -> str:
        """Get motivational message based on progress."""
        if progress_percentage >= 100:
            return "🎯 Congratulations! Goal completed!"
        elif progress_percentage >= 75:
            return "🔥 Almost there! Keep up the great work!"
        elif progress_percentage >= 50:
            return "💪 Halfway there! You're doing amazing!"
        elif progress_percentage >= 25:
            return "🌟 Great progress! Keep building that momentum!"
        else:
            return "🚀 Every step counts! You've got this!"
