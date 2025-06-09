from flask import Blueprint, render_template
from flask_login import current_user, login_required

from app import db
from app.models.goal import Goal
from app.models.transaction import Transaction

bp = Blueprint("main", __name__)


@bp.route("/")
@bp.route("/index")
def index():
    if not current_user.is_authenticated:
        return render_template("index.html")

    # Get recent transactions for dashboard
    recent_transactions = (
        Transaction.query.filter_by(user_id=current_user.id)
        .order_by(Transaction.date.desc(), Transaction.created_at.desc())
        .limit(5)
        .all()
    )

    # Calculate summary statistics
    total_income = (
        db.session.query(db.func.sum(Transaction.amount))
        .filter_by(user_id=current_user.id, type="income")
        .scalar()
        or 0
    )
    total_expenses = (
        db.session.query(db.func.sum(Transaction.amount))
        .filter_by(user_id=current_user.id, type="expense")
        .scalar()
        or 0
    )
    net_balance = total_income - total_expenses

    # Create financial summary object
    class FinancialSummary:
        def __init__(self, income, expenses, balance):
            self.total_income = income
            self.total_expenses = expenses
            self.net_balance = balance

    financial_summary = FinancialSummary(total_income, total_expenses, net_balance)

    # Get goal information for dashboard
    active_goals = (
        Goal.query.filter_by(user_id=current_user.id)
        .filter(Goal.status.in_(["active", "overdue"]))
        .limit(3)
        .all()
    )

    all_goals = Goal.query.filter_by(user_id=current_user.id).count()
    completed_goals = Goal.query.filter_by(
        user_id=current_user.id, status="completed"
    ).count()
    active_goals_count = (
        Goal.query.filter_by(user_id=current_user.id)
        .filter(Goal.status.in_(["active", "overdue"]))
        .count()
    )

    # Create goal summary object
    class GoalSummary:
        def __init__(self, active, completed, total):
            self.active_goals = active
            self.completed_goals = completed
            self.total_goals = total

    goal_summary = GoalSummary(active_goals_count, completed_goals, all_goals)

    return render_template(
        "index.html",
        recent_transactions=recent_transactions,
        financial_summary=financial_summary,
        goal_summary=goal_summary,
        active_goals=active_goals,
    )
