from django.contrib import admin, messages
from django.http import HttpResponse
from django.urls import path, reverse, NoReverseMatch
from django.utils.html import format_html
from django.apps import apps
import pandas as pd
import os
from tempfile import NamedTemporaryFile

from .models import *
from .utils import generate_invoice, send_invoice_email
from app.views.admin_dashboard import sales_dashboard


models = [Category, Product, OrderItem, ShippingAddress, Customer,
          CustomerMessage, Combo, ComboItem, WeightTracking, MealPlan, GuestOrder]
for model in models:
    admin.site.register(model)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'payment_method', 'complete', 'is_paid')
    list_filter = ('complete', 'is_paid')
    actions = ['mark_as_paid']

    def mark_as_paid(self, request, queryset):
        for order in queryset:
            if not order.is_paid:
                order.is_paid = True
                order.save()

                pdf_path = generate_invoice(order)


                if order.customer and order.customer.user and order.customer.user.email:
                    send_invoice_email(order.customer.user.email, pdf_path, order)
                    self.message_user(request, f" Invoice sent to {order.customer.user.email}", messages.SUCCESS)
                else:
                    self.message_user(request, "⚠ Customer email not found", messages.WARNING)
            else:
                self.message_user(request, f" Order {order.id} has been paid before", messages.ERROR)

    mark_as_paid.short_description = "Confirm payment & send invoice"

class CustomAdminSite(admin.AdminSite):
    site_header = "Product Management"
    site_title = "Admin Panel"
    index_title = "Welcome to Admin Dashboard"

    def get_urls(self):


        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(sales_dashboard), name='admin_dashboard'),
            path('export-excel/', self.admin_view(self.export_all_to_excel), name='export_excel'),
        ]
        return custom_urls + urls

    def dashboard_link(self):
        url = reverse('admin_dashboard')
        return format_html(f'<a href="{url}" class="button" '
                           'style="display:block; padding:10px; margin:10px 0; '
                           'background:#3498db; color:#fff; text-align:center; '
                           'border-radius:5px; text-decoration:none;">📊 Dashboard</a>')

    def export_all_to_excel(self, request):
        models = apps.get_models()

        with NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
            file_path = tmp_file.name
            with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
                for model in models:
                    model_name = model._meta.model_name
                    if model._meta.app_label == "admin":
                        continue
                    data = list(model.objects.all().values())
                    if data:
                        df = pd.DataFrame(data)
                        for col in df.select_dtypes(include=["datetime64[ns, UTC]", "datetime64"]):
                            df[col] = df[col].dt.tz_convert(None)
                        df.to_excel(writer, sheet_name=model_name, index=False)

            with open(file_path, "rb") as excel_file:
                response = HttpResponse(excel_file.read(),
                                        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                response["Content-Disposition"] = 'attachment; filename="database_export.xlsx"'

            os.remove(file_path)
            return response

    def export_excel_link(self):
        try:
            url = reverse('export_excel')
            print(f" Export Excel URL: {url}")
            return format_html(f'<a href="{url}" class="button" '
                               'style="display:block; padding:10px; margin:10px 0; '
                               'background:#2ecc71; color:#fff; text-align:center; '
                               'border-radius:5px; text-decoration:none;">📥 Xuất Excel</a>')
        except NoReverseMatch:
            print("Lỗi: URL 'export_excel' chưa được đăng ký.")
            return "Lỗi: URL 'export_excel' chưa được đăng ký."



admin_site = CustomAdminSite(name="quangvinh")
for model in models:
    admin_site.register(model)

admin_site.register(Order, OrderAdmin)
