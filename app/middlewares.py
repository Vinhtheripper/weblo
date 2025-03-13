# app/middleware.py
from django.contrib.auth import logout
from app.models import Order,Customer
class SeparateAdminAndFrontendSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Kiểm tra nếu người dùng đang truy cập admin
        if request.path.startswith('/admin/'):
            # Đảm bảo rằng session của frontend không bị ảnh hưởng
            if hasattr(request, 'user') and request.user.is_authenticated and not request.user.is_staff:
                logout(request)  # Đăng xuất người dùng frontend
        else:
            # Đảm bảo rằng session của admin không bị ảnh hưởng
            if hasattr(request, 'user') and request.user.is_authenticated and request.user.is_staff:
                logout(request)  # Đăng xuất admin

        response = self.get_response(request)
        return response



class CartMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.cartItems = 0
        if request.user.is_authenticated:
            try:
                if not hasattr(request.user, 'customer'):
                    customer = Customer.objects.create(user=request.user, name=request.user.username)
                else:
                    customer = request.user.customer

                order = Order.objects.get(customer=customer, complete=False)

                request.cartItems = order.get_cart_items
            except Order.DoesNotExist:
                pass  # Không có order nào, giữ cartItems = 0

        response = self.get_response(request)
        return response

