from datetime import datetime
from extensions import db


class HardDiskBackup(db.Model):
    __tablename__ = "HardDiskHistorical"

    id = db.Column(db.Integer, primary_key=True)

    disk_name = db.Column(db.String(200), nullable=False)
    serial_number = db.Column(db.String(50), index=True)
    file_name = db.Column(db.String(255), nullable=False)
    full_path = db.Column(db.Text)
    size_mb = db.Column(db.Float)
    modified = db.Column(db.DateTime)

    uploaded_by = db.Column(db.String(100))
    uploaded_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"<HardDiskBackup {self.file_name}>"


class ServerAsset(db.Model):
    __tablename__ = "ServerAssets"

    id = db.Column(db.Integer, primary_key=True)

    hostname = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(50), nullable=False)
    environment = db.Column(db.String(50), nullable=False)  # PROD / DR
    segment = db.Column(db.String(50), nullable=False)      # CORE / APP / DB
    os = db.Column(db.String(100))
    owner = db.Column(db.String(100))

    created_by = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    cpu = db.Column(db.String(50))        # e.g., "16 cores"
    ram = db.Column(db.String(50))        # e.g., "64 GB"
    storage = db.Column(db.String(50))    # e.g., "2 TB"