from collections import defaultdict
from datetime import datetime, timedelta

from app.models.goal import Goal
from app.models.transaction import Transaction


def get_spending_by_category_data(user_id, start_date=None, end_date=None):
    """Get spending data by category for Chart.js pie chart"""
    query = Transaction.query.filter_by(user_id=user_id, type="expense")

    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)

    transactions = query.all()

    # Aggregate by category
    category_totals = defaultdict(float)
    for transaction in transactions:
        category_totals[transaction.category] += transaction.amount

    # Prepare data for Chart.js
    data = {
        "labels": list(category_totals.keys()),
        "datasets": [
            {
                "data": list(category_totals.values()),
                "backgroundColor": [
                    "#FF6384",
                    "#36A2EB",
                    "#FFCE56",
                    "#4BC0C0",
                    "#9966FF",
                    "#FF9F40",
                    "#FF6384",
                    "#C9CBCF",
                    "#4BC0C0",
                    "#FF6384",
                    "#36A2EB",
                ][: len(category_totals)],
                "borderWidth": 2,
                "borderColor": "#fff",
            }
        ],
    }

    total_spending = sum(category_totals.values())

    return {
        "chart_data": data,
        "total_spending": total_spending,
        "category_count": len(category_totals),
    }


def get_income_vs_expenses_data(user_id, months=6):
    """Get income vs expenses data for Chart.js bar chart"""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=months * 30)

    transactions = (
        Transaction.query.filter_by(user_id=user_id)
        .filter(Transaction.date >= start_date)
        .filter(Transaction.date <= end_date)
        .order_by(Transaction.date)
        .all()
    )

    # Aggregate by month
    monthly_data = defaultdict(lambda: {"income": 0, "expenses": 0})

    for transaction in transactions:
        month_key = transaction.date.strftime("%Y-%m")
        if transaction.type == "income":
            monthly_data[month_key]["income"] += transaction.amount
        else:
            monthly_data[month_key]["expenses"] += transaction.amount

    # Prepare data for Chart.js
    months_list = sorted(monthly_data.keys())
    income_data = [monthly_data[month]["income"] for month in months_list]
    expense_data = [monthly_data[month]["expenses"] for month in months_list]
    month_labels = [
        datetime.strptime(m, "%Y-%m").strftime("%b %Y") for m in months_list
    ]

    data = {
        "labels": month_labels,
        "datasets": [
            {
                "label": "Income",
                "data": income_data,
                "backgroundColor": "rgba(46, 204, 113, 0.8)",
                "borderColor": "rgba(46, 204, 113, 1)",
                "borderWidth": 1,
            },
            {
                "label": "Expenses",
                "data": expense_data,
                "backgroundColor": "rgba(231, 76, 60, 0.8)",
                "borderColor": "rgba(231, 76, 60, 1)",
                "borderWidth": 1,
            },
        ],
    }

    return {
        "chart_data": data,
        "total_income": sum(income_data),
        "total_expenses": sum(expense_data),
        "net_savings": sum(income_data) - sum(expense_data),
    }


def get_goals_progress_data(user_id):
    """Get goals progress data for Chart.js horizontal bar chart"""
    goals = (
        Goal.query.filter_by(user_id=user_id)
        .filter(Goal.status.in_(["active", "completed"]))
        .order_by(Goal.deadline.asc())
        .all()
    )

    if not goals:
        return None

    # Prepare data
    goal_labels = [
        goal.title[:20] + "..." if len(goal.title) > 20 else goal.title
        for goal in goals
    ]
    progress_data = [goal.progress_percentage for goal in goals]

    # Color code based on progress
    background_colors = []
    for progress in progress_data:
        if progress >= 100:
            background_colors.append("rgba(46, 204, 113, 0.8)")  # Green for completed
        elif progress >= 75:
            background_colors.append(
                "rgba(243, 156, 18, 0.8)"
            )  # Orange for near completion
        elif progress >= 50:
            background_colors.append(
                "rgba(52, 152, 219, 0.8)"
            )  # Blue for moderate progress
        else:
            background_colors.append("rgba(231, 76, 60, 0.8)")  # Red for low progress

    data = {
        "labels": goal_labels,
        "datasets": [
            {
                "label": "Progress (%)",
                "data": progress_data,
                "backgroundColor": background_colors,
                "borderColor": [
                    color.replace("0.8", "1") for color in background_colors
                ],
                "borderWidth": 1,
            }
        ],
    }

    return {
        "chart_data": data,
        "total_goals": len(goals),
        "completed_goals": len([g for g in goals if g.progress_percentage >= 100]),
        "average_progress": (
            sum(progress_data) / len(progress_data) if progress_data else 0
        ),
    }


def get_savings_trend_data(user_id, months=12):
    """Get savings trend data for Chart.js line chart"""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=months * 30)

    transactions = (
        Transaction.query.filter_by(user_id=user_id)
        .filter(Transaction.date >= start_date)
        .filter(Transaction.date <= end_date)
        .order_by(Transaction.date)
        .all()
    )

    if not transactions:
        return None

    # Calculate monthly net savings
    monthly_savings = defaultdict(float)

    for transaction in transactions:
        month_key = transaction.date.strftime("%Y-%m")
        if transaction.type == "income":
            monthly_savings[month_key] += transaction.amount
        else:
            monthly_savings[month_key] -= transaction.amount

    # Convert to cumulative savings
    months_list = sorted(monthly_savings.keys())
    cumulative_savings = []
    monthly_net = []
    total = 0

    for month in months_list:
        monthly_amount = monthly_savings[month]
        total += monthly_amount
        cumulative_savings.append(total)
        monthly_net.append(monthly_amount)

    month_labels = [
        datetime.strptime(m, "%Y-%m").strftime("%b %Y") for m in months_list
    ]

    data = {
        "labels": month_labels,
        "datasets": [
            {
                "label": "Cumulative Savings",
                "data": cumulative_savings,
                "borderColor": "rgba(52, 152, 219, 1)",
                "backgroundColor": "rgba(52, 152, 219, 0.2)",
                "fill": True,
                "tension": 0.4,
            },
            {
                "label": "Monthly Net",
                "data": monthly_net,
                "borderColor": "rgba(46, 204, 113, 1)",
                "backgroundColor": "rgba(46, 204, 113, 0.8)",
                "type": "bar",
                "yAxisID": "y1",
            },
        ],
    }

    return {
        "chart_data": data,
        "current_savings": cumulative_savings[-1] if cumulative_savings else 0,
        "best_month": max(monthly_net) if monthly_net else 0,
        "worst_month": min(monthly_net) if monthly_net else 0,
    }


def get_transaction_summary_data(user_id, days=30):
    """Get recent transaction summary for dashboard widgets"""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)

    transactions = (
        Transaction.query.filter_by(user_id=user_id)
        .filter(Transaction.date >= start_date)
        .filter(Transaction.date <= end_date)
        .all()
    )

    # Calculate summaries
    total_income = sum(t.amount for t in transactions if t.type == "income")
    total_expenses = sum(t.amount for t in transactions if t.type == "expense")
    transaction_count = len(transactions)

    # Top spending categories
    expense_categories = defaultdict(float)
    for transaction in transactions:
        if transaction.type == "expense":
            expense_categories[transaction.category] += transaction.amount

    top_categories = sorted(
        expense_categories.items(), key=lambda x: x[1], reverse=True
    )[:5]

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_amount": total_income - total_expenses,
        "transaction_count": transaction_count,
        "top_spending_categories": top_categories,
        "period_days": days,
    }
