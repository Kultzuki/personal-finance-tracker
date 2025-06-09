from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash

from app import db
from app.forms.auth import LoginForm, RegistrationForm
from app.models.user import User

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        flash("You are already logged in!", "info")
        return redirect(url_for("main.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(
                username=form.username.data.lower().strip()
            )  # Normalize username
            user.set_password(form.password.data)  # Use the model method
            db.session.add(user)
            db.session.commit()

            flash(
                f"🎉 Welcome {form.username.data}! Your account has been created successfully. Please sign in to continue.",
                "success",
            )
            return redirect(url_for("auth.login"))

        except Exception as e:
            db.session.rollback()
            flash(
                "An error occurred while creating your account. Please try again.",
                "error",
            )

    else:
        # Flash form validation errors
        if form.errors:
            flash("Please correct the errors below and try again.", "error")

    return render_template("auth/register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash("You are already logged in!", "info")
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        # Try to find user by username
        user = User.query.filter_by(username=form.username.data.lower().strip()).first()

        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember_me.data)

            # Get next page or redirect to dashboard
            next_page = request.args.get("next")
            if next_page and next_page.startswith("/"):  # Security check
                flash(f"Welcome back, {user.username}! 👋", "success")
                return redirect(next_page)
            else:
                flash(
                    f"Welcome back, {user.username}! Ready to manage your finances? 💰",
                    "success",
                )
                return redirect(url_for("main.index"))
        else:
            flash(
                "❌ Invalid username or password. Please check your credentials and try again.",
                "error",
            )

    else:
        # Flash form validation errors
        if form.errors:
            flash("Please correct the errors below and try again.", "error")

    return render_template("auth/login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    username = current_user.username
    logout_user()
    flash(
        f"You have been successfully logged out. See you soon, {username}! 👋", "info"
    )
    return redirect(url_for("main.index"))
