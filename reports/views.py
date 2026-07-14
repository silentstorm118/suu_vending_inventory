import io
import math
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from items.models import Item

# Target stock level multiplier (e.g., 2x min_level is considered "good")
TARGET_MULTIPLIER = 2


@login_required
def generate_low_stock_report(request):
    # Fetch all items below their minimum threshold
    low_items = Item.objects.filter(level_in_backroom__lt=F("min_level"))

    if not low_items.exists():
        messages.info(request, "All items are currently at or above minimum stock levels.")
        return redirect("items:item_list")

    # Group items by vendor
    vendor_groups = {}

    for item in low_items:
        # Safely fetch vendor connection & packaging multiplier
        conn = None
        multiplier = 1
        vendor_name = "Unknown Vendor"

        if hasattr(item, "vendor_connections"):
            connections = item.vendor_connections.all()
            if connections.exists():
                conn = connections.first()
                multiplier = getattr(conn, "amount_received_per_order", 1) or 1
                vendor = getattr(conn, "vendor", None)
                vendor_name = vendor.name if vendor else "Unknown Vendor"

        if vendor_name not in vendor_groups:
            vendor_groups[vendor_name] = []

        current = item.level_in_backroom
        min_level = item.min_level
        target = int(min_level * TARGET_MULTIPLIER)
        units_needed = max(0, target - current)

        # ✅ Calculate cases/packages needed to reach target
        cases_needed = math.ceil(units_needed / multiplier) if multiplier > 1 else units_needed

        vendor_groups[vendor_name].append({
            "item": item.name,
            "current": current,
            "min": min_level,
            "target": target,
            "units_needed": units_needed,
            "multiplier": multiplier,
            "cases_needed": cases_needed
        })

    # Generate PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72
    )
    styles = getSampleStyleSheet()
    elements = []

    # Report Header
    elements.append(Paragraph("LOW STOCK PURCHASE REPORT", styles["Title"]))
    elements.append(Paragraph(
        f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')} | "
        f"Target Level: {TARGET_MULTIPLIER}x Minimum Threshold | Calculated in Cases/Packages",
        styles["Normal"]
    ))
    elements.append(Spacer(1, 20))

    # Build sections per vendor
    for vendor_name, items_data in vendor_groups.items():
        elements.append(Paragraph(f"Vendor: {vendor_name}", styles["Heading2"]))
        elements.append(Spacer(1, 10))

        # Updated table to show cases/packages instead of raw units
        table_data = [
            ["Item Name", "Current", "Target", "Cases to Order"],
        ]

        for data in items_data:
            # Format: "2 case(s) (48 units)"
            case_label = f"{data['cases_needed']} case{'s' if data['cases_needed'] != 1 else ''}"
            table_data.append([
                data["item"],
                str(data["current"]),
                str(data["target"]),
                f"{case_label}"
            ])

        table = Table(table_data)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 24))

    doc.build(elements)

    # Return as downloadable PDF
    filename = f"low_stock_report_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
