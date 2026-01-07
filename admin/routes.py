from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from models import User
from extensions import db
from decorators import admin_required
from utils.password_policy import validate_password

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ======================
# USER LIST
# ======================
@admin_bp.route("/users")
@login_required
@admin_required
def users():
    users = User.query.order_by(User.user_id).all()
    return render_template("admin/users.html", users=users)


# ======================
# CREATE USER
# ======================
@admin_bp.route("/users/create", methods=["GET", "POST"])
@login_required
@admin_required
def user_create():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        full_name = request.form.get("full_name")
        role = request.form.get("role", "viewer")

        # ✅ Password complexity enforcement
        error = validate_password(password)
        if error:
            flash(error, "danger")
            return redirect(url_for("admin.user_create"))

        # ✅ Prevent duplicate username
        if User.query.filter_by(username=username).first():
            flash("Username already exists", "danger")
            return redirect(url_for("admin.user_create"))

        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            full_name=full_name,
            role=role,
            is_active=True,
            must_change_password=True  # 🔐 FORCE RESET
        )

        db.session.add(user)
        db.session.commit()

        flash("User created successfully. User must change password at first login.", "success")
        return redirect(url_for("admin.users"))

    return render_template("admin/user_create.html")


# ======================
# EDIT USER
# ======================
@admin_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def user_edit(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        user.username = request.form.get("username", user.username)
        user.full_name = request.form.get("full_name", user.full_name)
        user.role = request.form.get("role", user.role)
        user.is_active = request.form.get("active") == "1"

        db.session.commit()
        flash("User updated successfully", "success")
        return redirect(url_for("admin.users"))
    
    return render_template("admin/user_edit.html", user=user)



# ======================
# DELETE USER (SAFE)
# ======================
@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
@admin_required
def user_delete(user_id):
    user = User.query.get_or_404(user_id)

    # Safety rule: admin cannot delete himself
    if user.user_id == current_user.user_id:
        flash("You cannot delete your own account", "danger")
        return redirect(url_for("admin.users"))

    db.session.delete(user)
    db.session.commit()
    flash("User deleted", "success")
    return redirect(url_for("admin.users"))


# ======================
# RESET PASSWORD
# ======================
@admin_bp.route("/users/<int:user_id>/reset-password", methods=["POST"])
@login_required
@admin_required
def reset_user_password(user_id):
    user = User.query.get_or_404(user_id)

    if user.username == "admin":
        flash("Cannot reset main admin password", "danger")
        return redirect(url_for("admin.users"))

    new_password = "P@ssw0rd"  # or generate randomly
    user.must_change_password = True
    user.password_hash = generate_password_hash(new_password)

    db.session.commit()

    flash(f"Password reset to: {new_password}", "warning")
    return redirect(url_for("admin.users"))