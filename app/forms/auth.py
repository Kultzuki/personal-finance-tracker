import re

from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, Regexp, ValidationError

from app.models.user import User


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(message="Username is required"),
            Length(
                min=3, max=20, message="Username must be between 3 and 20 characters"
            ),
            Regexp(
                "^[A-Za-z0-9_]+$",
                message="Username can only contain letters, numbers, and underscores",
            ),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password is required"),
            Length(min=8, message="Password must be at least 8 characters long"),
        ],
    )
    password2 = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(message="Please confirm your password"),
            EqualTo("password", message="Passwords must match"),
        ],
    )
    submit = SubmitField("Create Account")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                "This username is already taken. Please choose another."
            )

    def validate_password(self, password):
        """Basic password validation"""
        if not password.data:
            return

        # Check for minimum requirements
        if len(password.data) < 8:
            raise ValidationError("Password must be at least 8 characters long.")


class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(message="Username is required"),
            Length(min=3, max=20, message="Please enter a valid username"),
        ],
    )
    password = PasswordField(
        "Password", validators=[DataRequired(message="Password is required")]
    )
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")
