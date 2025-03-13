from .models import *
from django.contrib import admin
from django.contrib import messages
from .utils import generate_invoice, send_invoice_email
from django.urls import reverse
from django.utils.html import format_html
from app.views.admin_dashboard import sales_dashboard


admin.site.register(Category)
admin.site.register(Product)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
admin.site.register(Customer)
admin.site.register(CustomerMessage)
admin.site.register(Combo)
admin.site.register(ComboItem)
admin.site.register(WeightTracking)
admin.site.register(MealPlan)
admin.site.register(GuestOrder)



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


                if order.customer and order.customer.user.email:
                    send_invoice_email(order.customer.user.email, pdf_path, order)
                    self.message_user(request, f"✅ Invoice sent to {order.customer.user.email}", messages.SUCCESS)
                else:
                    self.message_user(request, "⚠ Customer email not found", messages.WARNING)
            else:
                self.message_user(request, f"❌ Order {order.id} has been paid before", messages.ERROR)

    mark_as_paid.short_description = "Confirm payment & send invoice"




class CustomAdminSite(admin.AdminSite):
    site_header = "Quản lý Bán Hàng"
    site_title = "Admin Panel"
    index_title = "Chào mừng đến với Admin Dashboard"

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(sales_dashboard), name='admin_dashboard'),
        ]
        return custom_urls + urls

    def dashboard_link(self):
        """Tạo nút xem Dashboard"""
        url = reverse('admin_dashboard')
        return format_html(f'<a href="{url}" class="button" style="display:block; padding:10px; margin:10px 0; background:#3498db; color:#fff; text-align:center; border-radius:5px; text-decoration:none;">📊 Xem Dashboard</a>')

admin_site = CustomAdminSite(name="quangvinh")


