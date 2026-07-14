from django.db import models
from django.utils import timezone


class Item(models.Model):
    name = models.CharField(max_length=255, unique=True)
    # vendor = models.ForeignKey(
    #     "vendors.Vendor",
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name="items",
    # )
    level_in_backroom = models.IntegerField(default=0)
    min_level = models.IntegerField(default=10)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_low(self):
        return self.level_in_backroom < self.min_level

    @property
    def is_out(self):
        """Helper to check if backroom is exactly zero."""
        return self.level_in_backroom == 0

    def __str__(self):
        return self.name


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ("ADD", "Stock Added"),
        ("REMOVE", "Stock Removed"),
        ("SALE", "Vending Sale"),  # Triggered by background task
        ("ADJUST", "Manual Adjustment"),
    ]

    SOURCE_CHOICES = [
        ("USER", "User/Manual"),
        ("TASK", "Background Task"),
    ]

    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name="transactions"
    )


    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default="USER")
    quantity = models.IntegerField()  # Negative for sales/removals, positive for adds
    timestamp = models.DateTimeField(default=timezone.now)
    note = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.type != "SALE":
                # Clamp backroom level at 0 to prevent negative stock
                new_level = self.item.level_in_backroom + self.quantity
                self.item.level_in_backroom = max(0, new_level)
                self.item.save()
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.item.name} | {self.type} | {self.quantity} ({self.source})"
