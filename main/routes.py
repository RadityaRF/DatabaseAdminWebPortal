from flask import Blueprint, render_template
from flask_login import login_required
from datetime import datetime

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
@main_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@main_bp.context_processor
def inject_year():
    return {
        "current_year": datetime.now().year
    }
