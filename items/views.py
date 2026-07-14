from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render

from .models import Item, Transaction
from .forms import ItemForm


@login_required
def item_list(request):
    items = Item.objects.all().order_by("name")

    # Updated to match your new "Backroom Only" logic
    out_of_stock = items.filter(level_in_backroom=0).count()
    low_stock = items.filter(
        level_in_backroom__lt=models.F("min_level"), level_in_backroom__gt=0
    ).count()

    return render(
        request,
        "items/items.html",
        {
            "items": items,
            "out_of_stock": out_of_stock,
            "low_stock": low_stock,
        },
    )


@login_required
def update_backroom(request, item_id):
    if request.method == "POST":
        item = get_object_or_404(Item, id=item_id)
        try:
            adjustment = int(request.POST.get("adjustment", 0))
            note = request.POST.get("note", "Manual Adjustment")

            if adjustment == 0:
                messages.warning(request, "Adjustment cannot be zero.")
                return redirect("items:item_list")

            # ✅ PREVENT NEGATIVE INVENTORY
            if adjustment < 0 and item.level_in_backroom + adjustment < 0:
                messages.error(
                    request,
                    f"Cannot remove {abs(adjustment)} units. Only {item.level_in_backroom} available in backroom."
                )
                return redirect("items:item_list")

            Transaction.objects.create(
                item=item,
                type="ADD" if adjustment > 0 else "REMOVE",
                source="USER",
                quantity=adjustment,
                note=note,
            )

            messages.success(request, f"Updated {item.name} by {adjustment} units.")
        except ValueError:
            messages.error(request, "Invalid adjustment amount.")

    return redirect("items:item_list")


@login_required
def create_product(request):
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New item created successfully!")
            return redirect("items:item_list")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = ItemForm()
    return render(request, 'items/create_item.html', {'form': form})