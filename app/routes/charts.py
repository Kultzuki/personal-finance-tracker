import base64
import io
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, render_template, request, send_file
from flask_login import current_user, login_required

from app.utils.charts import (
    create_goals_progress_chart,
    create_income_vs_expenses_chart,
    create_savings_trend_chart,
    create_spending_by_category_chart,
)
from app.utils.data_aggregation import (
    get_goals_progress_data,
    get_income_vs_expenses_data,
    get_savings_trend_data,
    get_spending_by_category_data,
    get_transaction_summary_data,
)

bp = Blueprint("charts", __name__, url_prefix="/charts")


@bp.route("/")
@login_required
def index():
    """Display the charts dashboard"""
    return render_template("charts/index.html")


# Matplotlib chart routes (backend generated images)
@bp.route("/spending-by-category.png")
@login_required
def spending_by_category_png():
    """Generate and serve spending by category chart as PNG"""
    # Get date range from query parameters
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    if end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    chart_base64 = create_spending_by_category_chart(
        current_user.id, start_date, end_date
    )

    if chart_base64:
        # Convert base64 back to bytes for serving
        chart_data = base64.b64decode(chart_base64)
        return send_file(
            io.BytesIO(chart_data), mimetype="image/png", as_attachment=False
        )
    else:
        # Return empty response if no data
        from flask import abort

        abort(404)


@bp.route("/income-vs-expenses.png")
@login_required
def income_vs_expenses_png():
    """Generate and serve income vs expenses chart as PNG"""
    months = request.args.get("months", 6, type=int)
    chart_base64 = create_income_vs_expenses_chart(current_user.id, months)

    if chart_base64:
        chart_data = base64.b64decode(chart_base64)
        return send_file(
            io.BytesIO(chart_data), mimetype="image/png", as_attachment=False
        )
    else:
        from flask import abort

        abort(404)


@bp.route("/goals-progress.png")
@login_required
def goals_progress_png():
    """Generate and serve goals progress chart as PNG"""
    chart_base64 = create_goals_progress_chart(current_user.id)

    if chart_base64:
        chart_data = base64.b64decode(chart_base64)
        return send_file(
            io.BytesIO(chart_data), mimetype="image/png", as_attachment=False
        )
    else:
        from flask import abort

        abort(404)


@bp.route("/savings-trend.png")
@login_required
def savings_trend_png():
    """Generate and serve savings trend chart as PNG"""
    months = request.args.get("months", 12, type=int)
    chart_base64 = create_savings_trend_chart(current_user.id, months)

    if chart_base64:
        chart_data = base64.b64decode(chart_base64)
        return send_file(
            io.BytesIO(chart_data), mimetype="image/png", as_attachment=False
        )
    else:
        from flask import abort

        abort(404)


# Chart.js data API routes (JSON data for frontend)
@bp.route("/api/spending-by-category")
@login_required
def api_spending_by_category():
    """Get spending by category data for Chart.js"""
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    if end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    data = get_spending_by_category_data(current_user.id, start_date, end_date)
    return jsonify(data)


@bp.route("/api/income-vs-expenses")
@login_required
def api_income_vs_expenses():
    """Get income vs expenses data for Chart.js"""
    months = request.args.get("months", 6, type=int)
    data = get_income_vs_expenses_data(current_user.id, months)
    return jsonify(data)


@bp.route("/api/goals-progress")
@login_required
def api_goals_progress():
    """Get goals progress data for Chart.js"""
    data = get_goals_progress_data(current_user.id)
    return jsonify(data)


@bp.route("/api/savings-trend")
@login_required
def api_savings_trend():
    """Get savings trend data for Chart.js"""
    months = request.args.get("months", 12, type=int)
    data = get_savings_trend_data(current_user.id, months)
    return jsonify(data)


@bp.route("/api/dashboard-summary")
@login_required
def api_dashboard_summary():
    """Get dashboard summary data"""
    days = request.args.get("days", 30, type=int)
    data = get_transaction_summary_data(current_user.id, days)
    return jsonify(data)


# Combined chart views
@bp.route("/spending-analysis")
@login_required
def spending_analysis():
    """Display spending analysis page with multiple charts"""
    return render_template("charts/spending_analysis.html")


@bp.route("/goals-dashboard")
@login_required
def goals_dashboard():
    """Display goals tracking dashboard"""
    return render_template("charts/goals_dashboard.html")


@bp.route("/financial-trends")
@login_required
def financial_trends():
    """Display financial trends and patterns"""
    return render_template("charts/financial_trends.html")
