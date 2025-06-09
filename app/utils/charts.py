import base64
import io
from collections import defaultdict
from datetime import datetime, timedelta

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg

from app import db
from app.models.goal import Goal
from app.models.transaction import Transaction

# Set matplotlib to use non-interactive backend
plt.switch_backend("Agg")


def create_spending_by_category_chart(user_id, start_date=None, end_date=None):
    """Generate a pie chart of spending by category using Matplotlib"""
    # Query expenses by category
    query = Transaction.query.filter_by(user_id=user_id, type="expense")

    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)

    transactions = query.all()

    if not transactions:
        return None

    # Aggregate spending by category
    category_totals = defaultdict(float)
    for transaction in transactions:
        category_totals[transaction.category] += transaction.amount

    # Prepare data for chart
    categories = list(category_totals.keys())
    amounts = list(category_totals.values())

    # Create the chart
    fig, ax = plt.subplots(figsize=(10, 8))
    colors = plt.cm.Set3(np.linspace(0, 1, len(categories)))

    wedges, texts, autotexts = ax.pie(
        amounts, labels=categories, autopct="%1.1f%%", colors=colors, startangle=90
    )

    # Customize the chart
    ax.set_title("Spending by Category", fontsize=16, fontweight="bold", pad=20)

    # Improve label formatting
    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontweight("bold")

    # Add total spending
    total_spending = sum(amounts)
    fig.suptitle(f"Total Spending: ${total_spending:,.2f}", fontsize=12, y=0.02)

    plt.tight_layout()

    # Convert to base64 string for web display
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format="png", dpi=150, bbox_inches="tight")
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
    plt.close()

    return img_base64


def create_income_vs_expenses_chart(user_id, months=6):
    """Generate a bar chart comparing income vs expenses over time"""
    # Calculate date range
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=months * 30)

    # Query transactions
    transactions = (
        Transaction.query.filter_by(user_id=user_id)
        .filter(Transaction.date >= start_date)
        .filter(Transaction.date <= end_date)
        .order_by(Transaction.date)
        .all()
    )

    if not transactions:
        return None

    # Aggregate by month
    monthly_data = defaultdict(lambda: {"income": 0, "expenses": 0})

    for transaction in transactions:
        month_key = transaction.date.strftime("%Y-%m")
        if transaction.type == "income":
            monthly_data[month_key]["income"] += transaction.amount
        else:
            monthly_data[month_key]["expenses"] += transaction.amount

    # Prepare data for chart
    months_list = sorted(monthly_data.keys())
    income_data = [monthly_data[month]["income"] for month in months_list]
    expense_data = [monthly_data[month]["expenses"] for month in months_list]

    # Create the chart
    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(months_list))
    width = 0.35

    bars1 = ax.bar(
        x - width / 2, income_data, width, label="Income", color="#2ecc71", alpha=0.8
    )
    bars2 = ax.bar(
        x + width / 2, expense_data, width, label="Expenses", color="#e74c3c", alpha=0.8
    )

    # Customize the chart
    ax.set_xlabel("Month", fontweight="bold")
    ax.set_ylabel("Amount ($)", fontweight="bold")
    ax.set_title("Income vs Expenses by Month", fontsize=16, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(
        [datetime.strptime(m, "%Y-%m").strftime("%b %Y") for m in months_list],
        rotation=45,
    )
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Add value labels on bars
    def add_value_labels(bars):
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height + max(income_data + expense_data) * 0.01,
                    f"${height:,.0f}",
                    ha="center",
                    va="bottom",
                    fontsize=8,
                )

    add_value_labels(bars1)
    add_value_labels(bars2)

    plt.tight_layout()

    # Convert to base64
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format="png", dpi=150, bbox_inches="tight")
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
    plt.close()

    return img_base64


def create_goals_progress_chart(user_id):
    """Generate a horizontal bar chart showing progress on financial goals"""
    goals = (
        Goal.query.filter_by(user_id=user_id)
        .filter(Goal.status.in_(["active", "completed"]))
        .order_by(Goal.deadline.asc())
        .all()
    )

    if not goals:
        return None

    # Prepare data
    goal_names = [
        goal.title[:20] + "..." if len(goal.title) > 20 else goal.title
        for goal in goals
    ]
    progress_percentages = [goal.progress_percentage for goal in goals]
    target_amounts = [goal.target_amount for goal in goals]

    # Create the chart
    fig, ax = plt.subplots(figsize=(12, max(6, len(goals) * 0.8)))

    # Create horizontal bars
    colors = [
        "#2ecc71" if p >= 100 else "#f39c12" if p >= 75 else "#e74c3c"
        for p in progress_percentages
    ]
    bars = ax.barh(goal_names, progress_percentages, color=colors, alpha=0.8)

    # Customize the chart
    ax.set_xlabel("Progress (%)", fontweight="bold")
    ax.set_title("Financial Goals Progress", fontsize=16, fontweight="bold", pad=20)
    ax.set_xlim(0, 100)

    # Add percentage labels
    for i, (bar, percentage, target) in enumerate(
        zip(bars, progress_percentages, target_amounts)
    ):
        width = bar.get_width()
        ax.text(
            width + 1,
            bar.get_y() + bar.get_height() / 2,
            f"{percentage:.1f}%",
            ha="left",
            va="center",
            fontweight="bold",
        )
        ax.text(
            -2,
            bar.get_y() + bar.get_height() / 2,
            f"${target:,.0f}",
            ha="right",
            va="center",
            fontsize=9,
            alpha=0.7,
        )

    # Add a 100% reference line
    ax.axvline(x=100, color="black", linestyle="--", alpha=0.5)
    ax.text(100, len(goals) - 0.5, "100%", ha="center", va="bottom", fontweight="bold")

    # Add grid
    ax.grid(True, axis="x", alpha=0.3)

    plt.tight_layout()

    # Convert to base64
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format="png", dpi=150, bbox_inches="tight")
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
    plt.close()

    return img_base64


def create_savings_trend_chart(user_id, months=12):
    """Generate a line chart showing savings trend over time"""
    # Calculate date range
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=months * 30)

    # Query transactions
    transactions = (
        Transaction.query.filter_by(user_id=user_id)
        .filter(Transaction.date >= start_date)
        .filter(Transaction.date <= end_date)
        .order_by(Transaction.date)
        .all()
    )

    if not transactions:
        return None

    # Calculate cumulative savings by month
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
    total = 0

    for month in months_list:
        total += monthly_savings[month]
        cumulative_savings.append(total)

    # Create the chart
    fig, ax = plt.subplots(figsize=(12, 6))

    dates = [datetime.strptime(m, "%Y-%m") for m in months_list]
    ax.plot(
        dates,
        cumulative_savings,
        marker="o",
        linewidth=2,
        markersize=6,
        color="#3498db",
    )

    # Fill area under curve
    ax.fill_between(dates, cumulative_savings, alpha=0.3, color="#3498db")

    # Customize the chart
    ax.set_xlabel("Month", fontweight="bold")
    ax.set_ylabel("Cumulative Savings ($)", fontweight="bold")
    ax.set_title("Savings Trend Over Time", fontsize=16, fontweight="bold")
    ax.grid(True, alpha=0.3)

    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.xticks(rotation=45)

    # Add value annotations for key points
    if cumulative_savings:
        # Annotate the latest value
        latest_value = cumulative_savings[-1]
        ax.annotate(
            f"${latest_value:,.0f}",
            xy=(dates[-1], latest_value),
            xytext=(10, 10),
            textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7),
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"),
        )

    plt.tight_layout()

    # Convert to base64
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format="png", dpi=150, bbox_inches="tight")
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
    plt.close()

    return img_base64
