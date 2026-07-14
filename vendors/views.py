from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from items.models import Item

from .models import Vendor, VendorItem


@login_required
def vendor_list(request):
    vendors = Vendor.objects.all().order_by("name")
    return render(request, "vendors/vendor_list.html", {"vendors": vendors})


@login_required
def vendor_add(request):
    if request.method == "POST":
        name = request.POST.get("name")
        website = request.POST.get("website")
        contact_info = request.POST.get("contact_info")

        Vendor.objects.create(name=name, website=website, contact_info=contact_info)
        messages.success(request, f"Vendor {name} created successfully.")
        return redirect("vendors:vendor_list")

    return render(request, "vendors/vendor_form.html")


@login_required
def vendor_edit(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    if request.method == "POST":
        vendor.name = request.POST.get("name")
        vendor.website = request.POST.get("website")
        vendor.contact_info = request.POST.get("contact_info")
        vendor.save()
        messages.success(request, f"Vendor {vendor.name} updated.")
        return redirect("vendors:vendor_list")

    return render(request, "vendors/vendor_form.html", {"vendor": vendor})


@login_required
def vendor_item_add(request):
    if request.method == "POST":
        vendor_id = request.POST.get("vendor")
        item_id = request.POST.get("item")

        # Convert strings from POST into numeric types
        try:
            cost = Decimal(request.POST.get("cost_per_order", "0"))
            amount = int(request.POST.get("amount_received_per_order", "1"))

            vendor = get_object_or_404(Vendor, id=vendor_id)
            item = get_object_or_404(Item, id=item_id)

            VendorItem.objects.create(
                vendor=vendor,
                item=item,
                cost_per_order=cost,
                amount_received_per_order=amount,
            )
            messages.success(request, f"Linked {item.name} to {vendor.name}.")
            return redirect("vendors:vendor_list")

        except (ValueError, InvalidOperation):
            messages.error(
                request, "Invalid numeric values provided for cost or amount."
            )
            return redirect("vendors:vendor_item_add")

    vendors = Vendor.objects.all()
    items = Item.objects.all()
    return render(
        request, "vendors/vendor_item_form.html", {"vendors": vendors, "items": items}
    )


@login_required
def vendor_detail(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    # Get all items linked to this vendor through VendorItem
    vendor_items = vendor.vendor_items.select_related("item").all()

    # Identify which items specifically need reordering
    # (Backroom level is less than the item's min_level)
    for vi in vendor_items:
        vi.needs_reorder = vi.item.level_in_backroom < vi.item.min_level

    return render(
        request,
        "vendors/vendor_detail.html",
        {"vendor": vendor, "vendor_items": vendor_items},
    )
