from django.contrib import admin

from .models import Vendor, VendorItem

# Register your models here.
admin.site.register(Vendor)
admin.site.register(VendorItem)
