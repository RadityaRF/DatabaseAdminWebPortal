from flask_login import current_user
from functools import wraps
from flask import abort

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            abort(403)
        return f(*args, **kwargs)
    return wrapper

def operator_or_admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role not in ["admin", "operator"]:
            abort(403)
        return f(*args, **kwargs)
    return decorated