from datetime import datetime

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.forms.transaction import DeleteTransactionForm, TransactionForm
from app.models.transaction import Transaction

bp = Blueprint("transactions", __name__, url_prefix="/transactions")


@bp.route("/")
@login_required
def index():
    """Display all transactions for the current user"""
    page = request.args.get("page", 1, type=int)

    # Get filter parameters
    transaction_type = request.args.get("type")
    category = request.args.get("category")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    # Build query with filters
    query = Transaction.query.filter_by(user_id=current_user.id)

    if transaction_type:
        query = query.filter_by(type=transaction_type)
    if category:
        query = query.filter_by(category=category)
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(Transaction.date >= start_date_obj)
        except ValueError:
            flash("Invalid start date format", "error")
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(Transaction.date <= end_date_obj)
        except ValueError:
            flash("Invalid end date format", "error")

    transactions = query.order_by(
        Transaction.date.desc(), Transaction.created_at.desc()
    ).paginate(page=page, per_page=20, error_out=False)

    # Calculate filtered totals
    filtered_transactions = query.all()
    total_income = sum(t.amount for t in filtered_transactions if t.type == "income")
    total_expenses = sum(t.amount for t in filtered_transactions if t.type == "expense")
    net_balance = total_income - total_expenses

    # Get all categories for filter dropdown
    categories = (
        db.session.query(Transaction.category)
        .filter_by(user_id=current_user.id)
        .distinct()
        .all()
    )
    categories = [cat[0] for cat in categories]

    # Create summary object
    class Summary:
        def __init__(self, income, expenses, balance):
            self.total_income = income
            self.total_expenses = expenses
            self.net_balance = balance

    summary = Summary(total_income, total_expenses, net_balance)

    return render_template(
        "transactions/index.html",
        transactions=transactions,
        summary=summary,
        categories=categories,
    )


@bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """Add a new transaction"""
    form = TransactionForm()

    # Update category choices based on transaction type
    if request.method == "POST" and form.type.data:
        if form.type.data == "income":
            form.category.choices = form.income_categories
        else:
            form.category.choices = form.expense_categories

    if form.validate_on_submit():
        try:
            transaction = Transaction(
                type=form.type.data,
                category=form.category.data,
                amount=float(form.amount.data),
                date=form.date.data,
                description=form.description.data,
                notes=form.notes.data,
                user_id=current_user.id,
            )
            db.session.add(transaction)
            db.session.commit()

            # Success message with emojis and details
            type_emoji = "💰" if form.type.data == "income" else "💸"
            flash(
                f'{type_emoji} {form.type.data.title()} of ${form.amount.data:,.2f} for "{form.description.data}" added successfully!',
                "success",
            )

            # Redirect to transaction list
            return redirect(url_for("transactions.index"))

        except Exception as e:
            db.session.rollback()
            flash(
                "❌ An error occurred while saving the transaction. Please try again.",
                "error",
            )

    else:
        # Flash validation errors
        if form.errors:
            flash("Please correct the errors below and try again.", "error")

    return render_template("transactions/create.html", form=form)


@bp.route("/<int:id>")
@login_required
def view(id):
    """View a specific transaction"""
    transaction = Transaction.query.filter_by(
        id=id, user_id=current_user.id
    ).first_or_404()
    return render_template("transactions/view.html", transaction=transaction)


@bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id):
    """Edit an existing transaction"""
    transaction = Transaction.query.filter_by(
        id=id, user_id=current_user.id
    ).first_or_404()
    form = TransactionForm(obj=transaction)

    # Set appropriate category choices based on transaction type
    if transaction.type == "income":
        form.category.choices = form.income_categories
    else:
        form.category.choices = form.expense_categories

    # Update category choices based on form submission
    if request.method == "POST" and form.type.data:
        if form.type.data == "income":
            form.category.choices = form.income_categories
        else:
            form.category.choices = form.expense_categories

    if form.validate_on_submit():
        try:
            # Store original values for comparison
            original_amount = transaction.amount
            original_type = transaction.type

            transaction.type = form.type.data
            transaction.category = form.category.data
            transaction.amount = float(form.amount.data)
            transaction.date = form.date.data
            transaction.description = form.description.data
            transaction.notes = form.notes.data
            db.session.commit()

            # Success message
            type_emoji = "💰" if form.type.data == "income" else "💸"
            flash(
                f'{type_emoji} Transaction "{form.description.data}" updated successfully!',
                "success",
            )
            return redirect(url_for("transactions.index"))

        except Exception as e:
            db.session.rollback()
            flash(
                "❌ An error occurred while updating the transaction. Please try again.",
                "error",
            )

    else:
        # Flash validation errors
        if form.errors:
            flash("Please correct the errors below and try again.", "error")

    return render_template("transactions/edit.html", form=form, transaction=transaction)


@bp.route("/<int:id>/delete", methods=["GET", "POST"])
@login_required
def delete(id):
    """Delete a transaction"""
    transaction = Transaction.query.filter_by(
        id=id, user_id=current_user.id
    ).first_or_404()

    if request.method == "POST":
        try:
            transaction_info = f'{transaction.type} of ${transaction.amount:,.2f} for "{transaction.description}"'
            type_emoji = "💰" if transaction.type == "income" else "💸"

            db.session.delete(transaction)
            db.session.commit()

            flash(
                f"🗑️ {type_emoji} {transaction_info} has been deleted successfully.",
                "success",
            )
            return redirect(url_for("transactions.index"))

        except Exception as e:
            db.session.rollback()
            flash(
                "❌ An error occurred while deleting the transaction. Please try again.",
                "error",
            )
            return redirect(url_for("transactions.index"))

    # GET request - show confirmation page
    return render_template("transactions/delete.html", transaction=transaction)


@bp.route("/api/categories/<transaction_type>")
@login_required
def get_categories(transaction_type):
    """API endpoint to get categories for a transaction type"""
    form = TransactionForm()

    if transaction_type == "income":
        categories = form.income_categories
    elif transaction_type == "expense":
        categories = form.expense_categories
    else:
        categories = []

    return jsonify(categories)
