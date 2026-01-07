import os
from urllib.parse import quote_plus

APP_VERSION = "V1.0"

class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

    DB_USER = quote_plus(os.getenv("DB_USER"))
    DB_PASSWORD = quote_plus(os.getenv("DB_PASSWORD"))

    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}"
        f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
        "?driver=ODBC+Driver+18+for+SQL+Server"
        "&Encrypt=yes"
        "&TrustServerCertificate=yes"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
