from datetime import date, datetime

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.forms.goal import DeleteGoalForm, GoalForm, SetProgressForm, UpdateProgressForm
from app.models.goal import Goal

bp = Blueprint("goals", __name__, url_prefix="/goals")


@bp.route("/")
@login_required
def index():
    """Display all goals for the current user"""
    goals = (
        Goal.query.filter_by(user_id=current_user.id)
        .order_by(Goal.deadline.asc(), Goal.created_at.desc())
        .all()
    )

    # Categorize goals
    active_goals = [g for g in goals if g.status == "active" and not g.is_completed]
    completed_goals = [g for g in goals if g.is_completed or g.status == "completed"]
    overdue_goals = [g for g in goals if g.is_overdue and g.status == "active"]

    # Calculate statistics
    total_goals = len(goals)
    total_target = sum(g.target_amount for g in goals)
    total_progress = sum(g.current_amount for g in goals)
    overall_progress = (total_progress / total_target * 100) if total_target > 0 else 0

    return render_template(
        "goals/index.html",
        active_goals=active_goals,
        completed_goals=completed_goals,
        overdue_goals=overdue_goals,
        total_goals=total_goals,
        total_target=total_target,
        total_progress=total_progress,
        overall_progress=overall_progress,
    )


@bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """Add a new goal"""
    form = GoalForm()

    if form.validate_on_submit():
        try:
            goal = Goal(
                name=form.name.data.strip(),
                description=(
                    form.description.data.strip() if form.description.data else None
                ),
                target_amount=float(form.target_amount.data),
                current_amount=(
                    float(form.current_amount.data) if form.current_amount.data else 0.0
                ),
                deadline=form.deadline.data,
                status=form.status.data,
                user_id=current_user.id,
            )
            db.session.add(goal)
            db.session.commit()

            # Success message with emoji and motivational text
            flash(
                f'🎯 Goal "{goal.name}" created successfully! Target: ${goal.target_amount:,.2f} by {goal.deadline.strftime("%B %d, %Y")}. You got this! 💪',
                "success",
            )
            return redirect(url_for("goals.index"))

        except Exception as e:
            db.session.rollback()
            flash(
                "❌ An error occurred while creating your goal. Please try again.",
                "error",
            )

    else:
        # Flash validation errors
        if form.errors:
            flash("Please correct the errors below and try again.", "error")

    return render_template("goals/create.html", form=form)


@bp.route("/<int:id>")
@login_required
def view(id):
    """View a specific goal with detailed progress"""
    goal = Goal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    update_form = UpdateProgressForm()
    set_form = SetProgressForm()

    return render_template(
        "goals/view.html", goal=goal, update_form=update_form, set_form=set_form
    )


@bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id):
    """Edit an existing goal"""
    goal = Goal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = GoalForm(obj=goal)

    if form.validate_on_submit():
        try:
            old_name = goal.name
            old_target = goal.target_amount

            goal.name = form.name.data.strip()
            goal.description = (
                form.description.data.strip() if form.description.data else None
            )
            goal.target_amount = float(form.target_amount.data)
            goal.update_progress(
                float(form.current_amount.data) if form.current_amount.data else 0.0
            )
            goal.deadline = form.deadline.data
            goal.status = form.status.data
            db.session.commit()

            # Success message with details of what changed
            changes = []
            if old_name != goal.name:
                changes.append(f'name to "{goal.name}"')
            if old_target != goal.target_amount:
                changes.append(f"target amount to ${goal.target_amount:,.2f}")

            if changes:
                change_text = " and ".join(changes)
                flash(
                    f"🎯 Goal updated successfully! Changed {change_text}.", "success"
                )
            else:
                flash(f'🎯 Goal "{goal.name}" updated successfully!', "success")

            return redirect(url_for("goals.index"))

        except Exception as e:
            db.session.rollback()
            flash(
                "❌ An error occurred while updating your goal. Please try again.",
                "error",
            )

    else:
        # Flash validation errors
        if form.errors:
            flash("Please correct the errors below and try again.", "error")

    return render_template("goals/edit.html", form=form, goal=goal)


@bp.route("/<int:id>/update-progress", methods=["POST"])
@login_required
def update_progress(id):
    """Add progress to a goal"""
    goal = Goal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = UpdateProgressForm()

    if form.validate_on_submit():
        try:
            old_progress = goal.progress_percentage
            old_amount = goal.current_amount

            goal.add_progress(float(form.amount.data))
            db.session.commit()

            # Check if goal was completed
            if goal.is_completed and old_progress < 100:
                flash(
                    f'🎉 CONGRATULATIONS! You\'ve completed your goal "{goal.name}"! 🏆 Amazing work reaching ${goal.target_amount:,.2f}!',
                    "success",
                )
            else:
                progress_increase = goal.progress_percentage - old_progress
                flash(
                    f'💰 Added ${form.amount.data:,.2f} to "{goal.name}". Progress: {goal.progress_percentage:.1f}% (+{progress_increase:.1f}%)',
                    "success",
                )

        except Exception as e:
            db.session.rollback()
            flash(
                "❌ An error occurred while updating progress. Please try again.",
                "error",
            )
    else:
        # Flash validation errors
        if form.errors:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"❌ {error}", "error")
        else:
            flash("❌ Error updating progress. Please check your input.", "error")

    return redirect(url_for("goals.index"))


@bp.route("/<int:id>/set-progress", methods=["POST"])
@login_required
def set_progress(id):
    """Set the current progress of a goal"""
    goal = Goal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = SetProgressForm()

    if form.validate_on_submit():
        try:
            old_progress = goal.progress_percentage

            goal.update_progress(float(form.current_amount.data))
            db.session.commit()

            # Check if goal was completed
            if goal.is_completed and old_progress < 100:
                flash(
                    f'🎉 CONGRATULATIONS! You\'ve completed your goal "{goal.name}"! 🏆 Amazing work reaching ${goal.target_amount:,.2f}!',
                    "success",
                )
            else:
                flash(
                    f'📊 Progress updated for "{goal.name}". Current progress: {goal.progress_percentage:.1f}% (${goal.current_amount:,.2f} of ${goal.target_amount:,.2f})',
                    "success",
                )

        except Exception as e:
            db.session.rollback()
            flash(
                "❌ An error occurred while setting progress. Please try again.",
                "error",
            )
    else:
        # Flash validation errors
        if form.errors:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"❌ {error}", "error")
        else:
            flash("❌ Error setting progress. Please check your input.", "error")

    return redirect(url_for("goals.index"))


@bp.route("/<int:id>/delete", methods=["GET", "POST"])
@login_required
def delete(id):
    """Delete a goal"""
    goal = Goal.query.filter_by(id=id, user_id=current_user.id).first_or_404()

    if request.method == "POST":
        try:
            goal_name = goal.name
            goal_amount = goal.target_amount

            db.session.delete(goal)
            db.session.commit()

            flash(
                f'🗑️ Goal "{goal_name}" (${goal_amount:,.2f}) has been deleted successfully.',
                "success",
            )
            return redirect(url_for("goals.index"))

        except Exception as e:
            db.session.rollback()
            flash(
                "❌ An error occurred while deleting the goal. Please try again.",
                "error",
            )
            return redirect(url_for("goals.index"))

    # GET request - show confirmation page
    return render_template("goals/delete.html", goal=goal)


@bp.route("/<int:id>/complete", methods=["POST"])
@login_required
def complete(id):
    """Mark a goal as completed"""
    goal = Goal.query.filter_by(id=id, user_id=current_user.id).first_or_404()

    try:
        goal.status = "completed"
        goal.current_amount = goal.target_amount  # Set to 100%
        db.session.commit()

        flash(
            f'🎉 AMAZING! Goal "{goal.name}" marked as completed! 🏆 You\'ve successfully reached your target of ${goal.target_amount:,.2f}! Time to celebrate! 🎊',
            "success",
        )
        return redirect(url_for("goals.index"))

    except Exception as e:
        db.session.rollback()
        flash(
            "❌ An error occurred while marking the goal as completed. Please try again.",
            "error",
        )
        return redirect(url_for("goals.index"))


@bp.route("/api/stats")
@login_required
def api_stats():
    """API endpoint for goal statistics"""
    goals = Goal.query.filter_by(user_id=current_user.id).all()

    stats = {
        "total_goals": len(goals),
        "active_goals": len([g for g in goals if g.status == "active"]),
        "completed_goals": len([g for g in goals if g.is_completed]),
        "overdue_goals": len([g for g in goals if g.is_overdue]),
        "total_target_amount": sum(g.target_amount for g in goals),
        "total_current_amount": sum(g.current_amount for g in goals),
        "overall_progress": 0,
    }

    if stats["total_target_amount"] > 0:
        stats["overall_progress"] = (
            stats["total_current_amount"] / stats["total_target_amount"]
        ) * 100

    return jsonify(stats)
