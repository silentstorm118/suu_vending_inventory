from django.db import models


class Vendor(models.Model):
    name = models.CharField(max_length=255, unique=True)
    website = models.URLField(blank=True, null=True)
    contact_info = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class VendorItem(models.Model):
    vendor = models.ForeignKey(
        Vendor, on_delete=models.CASCADE, related_name="vendor_items"
    )
    item = models.ForeignKey(
        "items.Item", on_delete=models.CASCADE, related_name="vendor_connections"
    )

    cost_per_order = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Cost to buy one unit/case"
    )
    amount_received_per_order = models.IntegerField(
        help_text="e.g., 24 (if you buy 1 case and get 24 cans)"
    )
    price_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Calculated price per individual item",
    )

    def save(self, *args, **kwargs):
        # Automatically calculate price per unit if not provided
        if self.cost_per_order and self.amount_received_per_order:
            self.price_per_unit = self.cost_per_order / self.amount_received_per_order
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.vendor.name} - {self.item.name}"
