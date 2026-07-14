from django.db import models
from django.utils import timezone
from items.models import Item
from vendors.models import Vendor


class Order(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("RECEIVED", "Received"),
        ("CANCELLED", "Cancelled"),
    ]

    order_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    received_at = models.DateTimeField(null=True, blank=True)

    def mark_as_received(self):
        """
        Updates backroom stock for all items in this order and
        prevents double-counting if called multiple times.
        """
        if self.status != "RECEIVED":
            for line_item in self.items.all():
                # We use the Transaction model to ensure an audit trail
                from items.models import Transaction

                Transaction.objects.create(
                    item=line_item.item,
                    type="ADD",
                    source="USER",
                    quantity=line_item.quantity_received,
                    note=f"Order #{self.order_number} Received",
                )
            self.status = "RECEIVED"
            self.received_at = timezone.now()
            self.save()

    def __str__(self):
        return f"Order {self.order_number} ({self.status})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True)
    quantity_ordered = models.IntegerField()
    quantity_received = models.IntegerField()  # e.g. 1 case = 24 units for the backroom
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.item.name} x {self.quantity_ordered}"


def mark_as_received(self):
    if self.status != "RECEIVED":
        # We import here to avoid circular import issues with items.models
        from items.models import Transaction

        for line_item in self.items.all():
            # Crucial: This creates the history record
            # which triggers the Item.level_in_backroom update
            Transaction.objects.create(
                item=line_item.item,
                type="ADD",
                source="USER",
                quantity=line_item.quantity_received,  # Ensure this isn't 0!
                note=f"Received Order {self.order_number}",
            )

        self.status = "RECEIVED"
        self.received_at = timezone.now()
        self.save()
