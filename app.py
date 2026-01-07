from flask import Flask, redirect, url_for, request
from flask_login import current_user
from dotenv import load_dotenv
from config import Config
from extensions import db, login_manager, migrate
from assets import assets_bp
from datetime import datetime


load_dotenv()




def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    login_manager.login_view = "auth.login"

    # 🔐 FORCE PASSWORD CHANGE
    @app.before_request
    def force_password_change():
        if (
            current_user.is_authenticated
            and current_user.must_change_password
            and request.endpoint not in (
                "auth.change_password",
                "auth.logout",
                "static",
            )
        ):
            return redirect(url_for("auth.change_password"))
        
    @app.context_processor
    def inject_app_meta():
        return {
            "app_version": app.config.get("APP_VERSION", "V1.0")
    }
    
    @app.context_processor
    def inject_server_time():
        return {
            "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    from auth.routes import auth_bp
    from main.routes import main_bp
    from admin.routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(assets_bp)

    return app

app = create_app()

if __name__ == "__main__":
    app.run()
