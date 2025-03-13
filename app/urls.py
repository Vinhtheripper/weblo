from django.urls import path
from app.views.general import home, Contact, Aboutus
from app.views.product import product_detail, combo_detail, category, search, menu
from app.views.user import register, loginPage, logoutPage,  change_password
from app.views.cart import *
from app.views.account import  meal_plan_view,my_account
from app.views.misc import redeem_points
from app.views.admin_dashboard import sales_dashboard

urlpatterns = [
    path('', home, name='home'),
    path('menu/', menu, name='menu'),
    path('login/', loginPage, name='login'),
    path('logout/', logoutPage, name='logout'),
    path("register/", register, name="register"),
    path("contact/", Contact, name="contact"),
    path("aboutus/", Aboutus, name="aboutus"),
    path("cart/", cart, name="cart"),
    path('checkout/', checkout, name='checkout'),
    path('update_item/', updateItem, name='update_item'),
    path('detail/', product_detail, name='detail'),
    path('search/', search, name='search'),
    path('payment/', payment, name='payment'),
    path('confirm-payment/', confirm_payment, name='confirm_payment'),
    path('payment_success/', payment_success, name='payment_success'),
    path("my_account/", my_account, name="my_account"),
    path('change-password/', change_password, name='change_password'),
    path('redeem_points/', redeem_points, name='redeem_points'),
    path('combo_detail/<int:id>/', combo_detail, name='combo_detail'),
    path('category/', category, name='category'),
    path('meal_plan_view/', meal_plan_view, name='meal_plan_view'),
    path('meal_plan_view/', meal_plan_view, name='meal_plan_view'),
    path('dashboard/', sales_dashboard, name='admin_dashboard'),
]
