from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from models import User
from extensions import db 
from utils.password_policy import validate_password

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()

        if not user:
            return render_template("login.html")

        if not user.is_active:
            return render_template("login.html")

        if not check_password_hash(
            user.password_hash, request.form["password"]
        ):
            return render_template("login.html")

        login_user(user)

        # 🚨 FORCE PASSWORD CHANGE
        if user.must_change_password:
            return redirect(url_for("auth.change_password"))

        return redirect(url_for("main.dashboard"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

@auth_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        new_password = request.form["password"]
        confirm = request.form["confirm_password"]

        if new_password != confirm:
            flash("Passwords do not match", "danger")
            return redirect(url_for("auth.change_password"))

        # 🔐 COMPLEXITY CHECK
        error = validate_password(new_password)
        if error:
            flash(error, "danger")
            return redirect(url_for("auth.change_password"))

        current_user.password_hash = generate_password_hash(new_password)
        current_user.must_change_password = False

        db.session.commit()

        flash("Password updated successfully", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("auth/change_password.html")

