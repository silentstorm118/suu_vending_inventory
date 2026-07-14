from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import F
from items.models import Item, Transaction
from orders.models import Order

@login_required
def dashboard_view(request):
    # Key metrics
    low_stock_count = Item.objects.filter(level_in_backroom__lt=F('min_level')).count()
    total_skus = Item.objects.count()
    pending_orders = Order.objects.filter(status='PENDING').count()

    # Recent activity & orders (limited to 5 for dashboard performance)
    recent_transactions = Transaction.objects.select_related('item').order_by('-timestamp')[:5]
    pending_orders_list = Order.objects.filter(status='PENDING').select_related().order_by('-created_at')[:5]

    return render(request, 'layouts/dashboard.html', {
        'low_stock_count': low_stock_count,
        'pending_orders': pending_orders,
        'total_skus': total_skus,
        'recent_transactions': recent_transactions,
        'pending_orders_list': pending_orders_list,
    })
