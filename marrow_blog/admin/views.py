from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
import pyotp # Uncomment if you implement pyotp for MFA

from .forms import LoginForm
from .models import AdminUser
from marrow_blog.extensions import db

admin_bp = Blueprint("admin", __name__, template_folder="../templates/admin", url_prefix="/admin")

@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        user = AdminUser.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            if user.is_mfa_enabled:
                if not form.token.data:
                    flash("MFA token is required.", "warning")
                    return render_template("login.html", form=form, title="Admin Login")
                totp = pyotp.TOTP(user.mfa_secret) # Uncomment for pyotp
                if not totp.verify(form.token.data):
                    flash("Invalid MFA token.", "error")
                    return render_template("login.html", form=form, title="Admin Login")
                # flash("MFA check placeholder: Successful (if token was provided and valid).", "info") # Placeholder

            login_user(user)
            flash("Logged in successfully.", "success")
            return redirect(url_for("admin.dashboard"))
        else:
            flash("Invalid username or password.", "error")
    return render_template("login.html", form=form, title="Admin Login")

@admin_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("admin.login"))

@admin_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", title="Admin Dashboard")
