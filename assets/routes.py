import pandas as pd
from flask import render_template, request, redirect, url_for, flash, Response, send_file
from flask_login import login_required, current_user
import io 
from reportlab.lib.pagesizes import A4 
from reportlab.pdfgen import canvas
from extensions import db
from .models import HardDiskBackup, ServerAsset
from . import assets_bp
from sqlalchemy import func 
from decorators import operator_or_admin_required
from collections import defaultdict


# =============================
# HARD DISK LIST
# =============================
@assets_bp.route("/hard-disk")
@login_required
def hard_disk_list():
    page = request.args.get("page", 1, type=int)
    per_page = 20

    # ===== Filters =====
    keyword = request.args.get("q", "").strip()
    start_date = request.args.get("start")
    end_date = request.args.get("end")

    query = HardDiskBackup.query

    # ===== Search =====
    if keyword:
        query = query.filter(
            HardDiskBackup.disk_name.ilike(f"%{keyword}%") |
            HardDiskBackup.serial_number.ilike(f"%{keyword}%") |
            HardDiskBackup.file_name.ilike(f"%{keyword}%")
        )

    # ===== Date Range =====
    if start_date:
        query = query.filter(HardDiskBackup.modified >= start_date)

    if end_date:
        query = query.filter(HardDiskBackup.modified <= end_date)

    pagination = (
        query
        .order_by(HardDiskBackup.id.asc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    # ===== Summary (filtered) =====
    summary = (
        db.session.query(
            HardDiskBackup.disk_name,
            HardDiskBackup.serial_number,
            func.count().label("total_files"),
            func.sum(HardDiskBackup.size_mb).label("total_size_mb"),
            func.max(HardDiskBackup.modified).label("latest_backup"),
        )
        .group_by(
            HardDiskBackup.disk_name,
            HardDiskBackup.serial_number
        )
        .all()
    )

    return render_template(
        "assets/hard_disk_list.html",
        data=pagination.items,
        pagination=pagination,
        summary=summary,
        keyword=keyword,
        start_date=start_date,
        end_date=end_date,
    )

# =============================
# UPLOAD CSV FORM
# =============================
@assets_bp.route("/hard-disk/upload", methods=["GET", "POST"])
@login_required
def hard_disk_upload():

    if request.method == "POST":
        file = request.files.get("file")

        if not file or not file.filename.endswith(".csv"):
            flash("Please upload a valid CSV file", "danger")
            return redirect(request.url)

        try:
            df = pd.read_csv(file)

            # === YOUR EXISTING LOGIC (UNCHANGED) ===
            df["SerialNumber"] = df["SerialNumber"].astype(str).str[-8:]

            df = df.rename(columns={"SizeMB": "Size"})[
                ["DiskName", "SerialNumber", "FileName", "FullPath", "Size", "Modified"]
            ]

            df["Modified"] = pd.to_datetime(df["Modified"])

            # === INSERT INTO DB ===
            for _, row in df.iterrows():
                record = HardDiskBackup(
                    disk_name=row["DiskName"],
                    serial_number=row["SerialNumber"],
                    file_name=row["FileName"],
                    full_path=row["FullPath"],
                    size_mb=row["Size"],
                    modified=row["Modified"],
                    uploaded_by=current_user.username
                )
                db.session.add(record)

            db.session.commit()
            flash("Hard disk data uploaded successfully", "success")

            return redirect(url_for("assets.hard_disk_list"))

        except Exception as e:
            db.session.rollback()
            flash(f"CSV processing failed: {e}", "danger")

    return render_template("hard_disk_upload.html")

# =============================
# EXPORT DATA HARD DISK
# =============================
@assets_bp.route("/hard-disk/export/<string:fmt>")
@login_required
def export_hard_disk(fmt):

    serial = request.args.get("serial")

    query = HardDiskBackup.query

    # ✅ Filter by Serial Number (optional)
    if serial:
        query = query.filter(HardDiskBackup.serial_number == serial)

    query = query.order_by(HardDiskBackup.modified.desc())

    df = pd.read_sql(query.statement, db.engine)

    if df.empty:
        flash("No data found for export", "warning")
        return redirect(url_for("assets.hard_disk_list"))

    # ================= CSV =================
    if fmt == "csv":
        output = io.StringIO()
        df.to_csv(output, index=False)

        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={
                "Content-Disposition": (
                    f"attachment; filename=hard_disk_{serial or 'all'}.csv"
                )
            }
        )

    # ================= XLSX =================
    elif fmt == "xlsx":
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="HardDisk")

        output.seek(0)
        return Response(
            output,
            mimetype=(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
            headers={
                "Content-Disposition": (
                    f"attachment; filename=hard_disk_{serial or 'all'}.xlsx"
                )
            }
        )

    # ================= PDF =================
    elif fmt == "pdf":
        from reportlab.platypus import (
            SimpleDocTemplate, Table, TableStyle, Paragraph
        )
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet

        output = io.BytesIO()

        doc = SimpleDocTemplate(
            output,
            pagesize=landscape(A4),
            rightMargin=20,
            leftMargin=20,
            topMargin=20,
            bottomMargin=20,
        )

        styles = getSampleStyleSheet()
        elements = []

        # ===== Title =====
        elements.append(
            Paragraph("Hard Disk Cold Storage Report", styles["Title"])
        )

        # ===== Table Data =====
        table_data = [df.columns.tolist()] + df.values.tolist()

        table = Table(
            table_data,
            repeatRows=1,
            colWidths=[
                80,   # disk_name
                80,   # serial
                140,  # file_name
                180,  # full_path
                70,   # size_mb
                110,  # modified
                90,   # uploaded_by
                110,  # uploaded_at
            ],
        )

        table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (4, 1), (4, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
            ])
        )

        elements.append(table)
        doc.build(elements)

        output.seek(0)

        return Response(
            output,
            mimetype="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=hard_disk_backup.pdf"
            }
        )



# =========================
# SERVER LIST (GROUPED)
# =========================
@assets_bp.route("/servers")
@login_required
def server_list():

    segment_filter = request.args.get("segment")
    env_filter = request.args.get("env")
    search = request.args.get("q")

    query = ServerAsset.query
    if segment_filter:
        query = query.filter(ServerAsset.segment == segment_filter)
    if env_filter:
        query = query.filter(ServerAsset.environment == env_filter)
    if search:
        query = query.filter(ServerAsset.hostname.ilike(f"%{search}%"))

    servers = query.order_by(ServerAsset.segment, ServerAsset.hostname).all()

    # ================= Group servers and calculate totals =================
    grouped = defaultdict(list)
    segment_totals = defaultdict(lambda: {"cpu": 0, "ram_gb": 0, "storage_gb": 0})

    for s in servers:
        grouped[s.segment].append(s)

        # CPU
        try:
            segment_totals[s.segment]["cpu"] += int(s.cpu.split()[0]) if s.cpu else 0
        except:
            segment_totals[s.segment]["cpu"] += 0

        # RAM in GB
        try:
            segment_totals[s.segment]["ram_gb"] += int(s.ram.split()[0]) if s.ram else 0
        except:
            segment_totals[s.segment]["ram_gb"] += 0

        # Storage in GB
        try:
            segment_totals[s.segment]["storage_gb"] += int(s.storage.split()[0]) if s.storage else 0
        except:
            segment_totals[s.segment]["storage_gb"] += 0

    # Convert RAM and Storage to TB for display
    for seg, totals in segment_totals.items():
        totals["ram_tb"] = round(totals["ram_gb"] / 1024, 2)
        totals["storage_tb"] = round(totals["storage_gb"] / 1024, 2)

    # ===== Dashboard counters =====
    counters = {
        "total": len(servers),
        "prod": sum(1 for s in servers if s.environment=="Production"),
        "dr": sum(1 for s in servers if s.environment=="Disaster Recovery"),
        "by_segment": {seg: len(lst) for seg, lst in grouped.items()}
    }

    return render_template(
        "assets/server_list.html",
        grouped=grouped,
        segment_totals=segment_totals,
        counters=counters
    )


# =========================
# CREATE SERVER
# =========================
@assets_bp.route("/servers/create", methods=["GET", "POST"])
@login_required
@operator_or_admin_required
def server_create():

    if request.method == "POST":
        server = ServerAsset(
            hostname=request.form["hostname"],
            ip_address=request.form["ip_address"],
            environment=request.form["environment"],
            segment=request.form["segment"],
            os=request.form.get("os"),
            owner=request.form.get("owner"),
            cpu=int(request.form.get("cpu") or 0),
            ram=int(request.form.get("ram") or 0),
            storage=int(request.form.get("storage") or 0),
            created_by=current_user.username
        )


        db.session.add(server)
        db.session.commit()

        flash("Server registered successfully", "success")
        return redirect(url_for("assets.server_list"))

    return render_template("assets/server_form.html")

# =====================================================
# DELETE SERVER (CONFIRMATION MODAL)
# =====================================================
@assets_bp.route("/servers/<int:id>/delete", methods=["POST"])
@login_required
@operator_or_admin_required
def server_delete(id):
    server = ServerAsset.query.get_or_404(id)

    db.session.delete(server)
    db.session.commit()

    flash("Server deleted successfully", "warning")
    return redirect(url_for("assets.server_list"))

# =====================================================
# EDIT SERVER (SAME FORM)
# =====================================================
@assets_bp.route("/servers/<int:id>/edit", methods=["GET", "POST"])
@login_required
@operator_or_admin_required
def server_edit(id):
    server = ServerAsset.query.get_or_404(id)

    if request.method == "POST":
        server.hostname = request.form["hostname"]
        server.ip_address = request.form["ip_address"]
        server.environment = request.form["environment"]
        server.segment = request.form["segment"]
        server.os = request.form.get("os")
        server.owner = request.form.get("owner")
        server.cpu = int(request.form.get("cpu") or 0)
        server.ram = int(request.form.get("ram") or 0)
        server.storage = int(request.form.get("storage") or 0)

        db.session.commit()
        flash("Server updated successfully", "success")
        return redirect(url_for("assets.server_list"))

    return render_template(
        "assets/server_form.html",
        server=server,
        mode="edit"
    )