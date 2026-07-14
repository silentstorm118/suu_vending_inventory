import uuid
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from items.models import Item
from vendors.models import Vendor

from .models import Order, OrderItem


@login_required
def order_list(request):
    orders = Order.objects.all().order_by("-created_at")
    return render(request, "orders/order_list.html", {"orders": orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    # line_items will contain the OrderItem objects (item name, qty, etc.)
    line_items = order.items.all()
    return render(
        request, "orders/order_detail.html", {"order": order, "items": line_items}
    )


@login_required
def order_add(request):
    if request.method == "POST":
        item_ids = request.POST.getlist("item[]")
        quantities = request.POST.getlist("quantity[]")
        vendor_id = request.POST.get("vendor")
        custom_po = request.POST.get("po_number", "").strip()

        if not item_ids or not vendor_id:
            messages.error(request, "Please select a vendor and at least one item.")
            return redirect("orders:order_add")

        try:
            with transaction.atomic():
                # Use custom PO if provided, otherwise auto-generate
                po_number = custom_po if custom_po else f"PO-{uuid.uuid4().hex[:6].upper()}"

                # Prevent duplicate PO numbers with a friendly error
                if Order.objects.filter(order_number=po_number).exists():
                    messages.error(request, "This Purchase Order number already exists. Please use a unique number or leave it blank.")
                    return redirect("orders:order_add")

                vendor = Vendor.objects.get(id=vendor_id)

                order = Order.objects.create(
                    order_number=po_number,
                    status="PENDING",
                    total_price=Decimal("0.00"),
                )

                total_order_price = Decimal("0.00")

                for i in range(len(item_ids)):
                    curr_item_id = item_ids[i]
                    if not curr_item_id:
                        continue  # Skip empty rows

                    item = Item.objects.get(id=curr_item_id)

                    try:
                        qty_ordered = int(quantities[i])
                    except (ValueError, TypeError):
                        qty_ordered = 1

                    connection = item.vendor_connections.filter(vendor=vendor).first()

                    if connection:
                        multiplier = connection.amount_received_per_order
                        cost_per_case = connection.cost_per_order
                    else:
                        multiplier = 1
                        cost_per_case = Decimal("0.00")

                    qty_received = qty_ordered * multiplier
                    line_price = Decimal(str(cost_per_case)) * qty_ordered

                    OrderItem.objects.create(
                        order=order,
                        item=item,
                        vendor=vendor,
                        quantity_ordered=qty_ordered,
                        quantity_received=qty_received,
                        price_at_order=line_price,
                    )

                    total_order_price += line_price

                order.total_price = total_order_price
                order.save()

            messages.success(request, f"Order {po_number} created successfully!")
            return redirect("orders:order_list")

        except Exception as e:
            messages.error(request, f"Error creating order: {str(e)}")
            return redirect("orders:order_add")

    # GET Request: Prepare data for dropdowns
    context = {
        "vendors": Vendor.objects.all().order_by("name"),
        "items": Item.objects.filter(vendor_connections__isnull=False)
        .distinct()
        .order_by("name"),
    }
    return render(request, "orders/order_form.html", context)



@login_required
def receive_order(request, order_id):
    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id)

        if order.status == "PENDING":
            # This is the line that actually runs the code above
            order.mark_as_received()
            messages.success(
                request, f"Success! Backroom updated for {order.order_number}."
            )
        else:
            messages.warning(request, "This order was already received.")

    return redirect("orders:order_list")
