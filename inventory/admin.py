from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection, transaction
import datetime
from inventory.models import (
    Warehouse,
    Inventory,
    InventoryTransaction,
    StockTransfer,
    StockTransferItems,
    DemandForecast,
)


class StockTransferItemsInline(admin.TabularInline):
    model = StockTransferItems
    extra = 1
    raw_id_fields = ("variant",)


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "city", "state", "is_active", "created_at")
    list_filter = ("is_active", "city", "state")
    search_fields = ("name", "code", "city", "state")
    ordering = ("name",)


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = (
        "variant",
        "warehouse",
        "available_quantity",
        "reserved_quantity",
        "damaged_quantity",
        "incoming_quantity",
    )
    list_filter = ("warehouse",)
    search_fields = ("variant__sku", "warehouse__name")
    raw_id_fields = ("variant", "warehouse")


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "variant",
        "warehouse",
        "transaction_type",
        "quantity",
        "created_at",
    )
    list_filter = ("transaction_type", "warehouse")
    search_fields = ("variant__sku", "warehouse__name")
    raw_id_fields = ("variant", "warehouse")
    date_hierarchy = "created_at"


@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    list_display = (
        "from_warehouse",
        "to_warehouse",
        "status",
        "shipped_at",
        "receiced_at",
    )
    list_filter = ("status", "from_warehouse", "to_warehouse")
    search_fields = ("from_warehouse__name", "to_warehouse__name")
    raw_id_fields = ("from_warehouse", "to_warehouse")
    inlines = (StockTransferItemsInline,)
    date_hierarchy = "created_at"


@admin.register(StockTransferItems)
class StockTransferItemsAdmin(admin.ModelAdmin):
    list_display = ("transfer", "variant", "quantity")
    search_fields = ("transfer__id", "variant__sku")
    raw_id_fields = ("transfer", "variant")


@admin.register(DemandForecast)
class DemandForecastAdmin(admin.ModelAdmin):
    list_display = ("item_label", "item_type", "forecast_date", "predicted_quantity")
    list_filter = ("item_type", "forecast_date")
    search_fields = ("item_label", "item_id")
    date_hierarchy = "forecast_date"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_site.admin_view(self.dashboard_view), name='inventory_demandforecast_dashboard'),
            path('sync/', self.admin_site.admin_view(self.sync_forecasts_view), name='inventory_demandforecast_sync'),
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        selected_item_id = request.GET.get('item_id')
        
        # Get list of items with forecasts
        items = DemandForecast.objects.values('item_id', 'item_label', 'item_type').distinct()
        
        selected_item = None
        history_data = []
        forecast_data = []
        kpis = {
            'total_demand': 0,
            'peak_demand': 0,
            'avg_demand': 0,
        }
        
        if items:
            if not selected_item_id:
                selected_item_id = str(items[0]['item_id'])
                selected_item = items[0]
            else:
                for item in items:
                    if str(item['item_id']) == selected_item_id:
                        selected_item = item
                        break
                if not selected_item:
                    selected_item_id = str(items[0]['item_id'])
                    selected_item = items[0]
            
            # Fetch historical actuals from ml.analytics_view
            # Find max date of order in ml.analytics_view to anchor history
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT MAX(order_created_at)::date 
                    FROM ml.analytics_view 
                    WHERE item_id = %s
                """, [selected_item_id])
                row = cursor.fetchone()
                end_date = row[0] if (row and row[0]) else datetime.date(2027, 5, 26)
                start_date = end_date - datetime.timedelta(days=30)
                
                cursor.execute("""
                    SELECT order_created_at::date AS ds, SUM(quantity) AS y
                    FROM ml.analytics_view
                    WHERE item_id = %s AND order_created_at::date BETWEEN %s AND %s
                    GROUP BY ds
                    ORDER BY ds
                """, [selected_item_id, start_date, end_date])
                history_rows = cursor.fetchall()
            
            history_data = [
                {'date': r[0].strftime('%Y-%m-%d'), 'quantity': float(r[1])}
                for r in history_rows
            ]
            
            # Fetch forecasts from DemandForecast
            forecasts = DemandForecast.objects.filter(item_id=selected_item_id).order_by('forecast_date')
            forecast_data = [
                {'date': f.forecast_date.strftime('%Y-%m-%d'), 'quantity': float(f.predicted_quantity)}
                for f in forecasts
            ]
            
            if forecast_data:
                quantities = [f['quantity'] for f in forecast_data]
                kpis['total_demand'] = round(sum(quantities), 2)
                kpis['peak_demand'] = round(max(quantities), 2)
                kpis['avg_demand'] = round(sum(quantities) / len(quantities), 2)
        
        context = {
            **self.admin_site.each_context(request),
            'title': "Demand Forecasting Dashboard",
            'items': items,
            'selected_item': selected_item,
            'history_data': history_data,
            'forecast_data': forecast_data,
            'kpis': kpis,
        }
        return render(request, 'admin/inventory/demandforecast/dashboard.html', context)

    def sync_forecasts_view(self, request):
        import requests
        try:
            # Call FastAPI POST /forecast/trigger endpoint
            response = requests.post("http://127.0.0.1:8001/forecast/trigger?horizon_days=14", timeout=60)
            if response.status_code == 200:
                data = response.json()
                forecasts_data = data.get("forecasts", [])
                
                with transaction.atomic():
                    DemandForecast.objects.all().delete()
                    
                    to_create = []
                    for item in forecasts_data:
                        item_id = item.get("item_id")
                        item_label = item.get("item_label")
                        item_type = item.get("item_type")
                        for pred in item.get("predictions", []):
                            to_create.append(DemandForecast(
                                item_id=item_id,
                                item_label=item_label,
                                item_type=item_type,
                                forecast_date=pred.get("date"),
                                predicted_quantity=pred.get("quantity")
                            ))
                    DemandForecast.objects.bulk_create(to_create)
                
                self.message_user(request, f"Successfully synchronized forecasts for {len(forecasts_data)} items.", messages.SUCCESS)
            else:
                self.message_user(request, f"FastAPI forecasting service returned error: {response.text}", messages.ERROR)
        except Exception as e:
            self.message_user(request, f"Failed to connect to FastAPI forecasting service: {str(e)}", messages.ERROR)
        
        return redirect("admin:inventory_demandforecast_dashboard")

