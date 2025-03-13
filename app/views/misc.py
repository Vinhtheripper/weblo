from django.shortcuts import  redirect
from app.models import *
from django.contrib import messages
from django.http import JsonResponse

def redeem_points(request):
    if not request.user.is_authenticated or not hasattr(request.user, "customer"):
        messages.error(request, "Bạn cần đăng nhập để đổi điểm.")
        return redirect("my_account")

    customer = request.user.customer
    order = Order.objects.filter(customer=customer, complete=False).first()

    if not order:
        messages.warning(request, "Bạn chưa có đơn hàng để đổi điểm.")
        return redirect("my_account")

    if customer.redeem_reward():
        order.used_reward = True
        order.save()
        messages.success(request, "Bạn đã đổi điểm thành công!")
    else:
        messages.warning(request, "Bạn chưa đủ điểm để đổi thưởng.")

    return redirect("my_account")









