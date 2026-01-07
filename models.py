from app import db, login_manager
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    role = db.Column(db.String(20), default="viewer")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    must_change_password = db.Column(db.Boolean, default=False)

    def get_id(self):
        return str(self.user_id)
    
    # For Admin Check
    def is_admin(self):
        return self.role == "admin"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
