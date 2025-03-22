from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django import forms
from decimal import Decimal, ROUND_HALF_UP
from django.utils.timezone import now

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Current password'}),
        label="Current password"
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New password'}),
        label="New password"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Repeat new password'}),
        label="Repeat new password"
    )


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, null=True)
    customer_image = models.ImageField(upload_to='Profile/', null=True, blank=True)
    points = models.IntegerField(default=0)


    def __str__(self):
        return self.name if self.name else f"Customer {self.id}"

    @property
    def imageURL(self):
        try:
            url = self.customer_image.url
        except:
            url = ''
        return url



    def can_redeem_reward(self):
        return self.points >= 10

    def redeem_reward(self):

        if self.can_redeem_reward():
            self.points -= 10
            self.save()
            return True
        return False


class Category(models.Model):
    sub_category = models.ForeignKey('self', on_delete=models.CASCADE, related_name='sub_categories', null=True, blank=True)
    is_sub = models.BooleanField(default=False)
    name = models.CharField(max_length=200, null=True)
    slug = models.SlugField(max_length=200, unique=True)
    description= models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

class BaseProduct(models.Model):
    name = models.CharField(max_length=200, null=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    detail = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def imageURL(self):
        try:
            return self.image.url
        except:
            return ''


class Product(BaseProduct):
    category = models.ManyToManyField(Category, related_name='products')
    price = models.FloatField()
    digital = models.BooleanField(default=False, null=True, blank=False)
    calories = models.IntegerField(default=0)
    protein = models.FloatField(default=0)
    carbs = models.FloatField(default=0)
    fat = models.FloatField(default=0)
    sale = models.BooleanField(default=False)
    discount_percentage = models.FloatField(default=0, null=True, blank=True)
    sale_price = models.FloatField(default=0, null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def final_price(self):
        if self.sale:
            if self.sale_price and self.sale_price > 0:
                return self.sale_price
            elif self.discount_percentage and self.discount_percentage > 0:
                return Decimal(self.price) * (1 - Decimal(self.discount_percentage) / 100)

        return Decimal(self.price)


class Combo(BaseProduct):
    products = models.ManyToManyField(Product, through='ComboItem')
    discount_percentage = models.FloatField(default=0)
    def __str__(self):
        return self.name

    @property
    def get_combo_price(self):
        """Tính giá combo dựa trên tổng giá sản phẩm trừ đi % giảm giá"""
        total_price = sum(item.product.price * item.quantity for item in self.comboitem_set.all())
        discount_amount = (total_price * self.discount_percentage) / 100
        return Decimal(total_price - discount_amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class ComboItem(models.Model):
    combo = models.ForeignKey(Combo, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.combo.name} - {self.product.name} x{self.quantity}"



class Order(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('momo', 'Momo'),
        ('vnpay', 'VNPay'),
        ('bank', 'Bank Transfer'),
]
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    date_order = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    transaction_id = models.CharField(max_length=200, null=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    used_reward=models.BooleanField(default=False)
    is_scheduled = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id} - {'Paid' if self.is_paid else 'Pending'}"

    @property
    def get_cart_items(self):
        order_items = self.orderitem_set.all()
        return sum([item.quantity for item in order_items])


    @property
    def get_cart_total(self):
        order_items = self.orderitem_set.all()
        total = sum([Decimal(str(item.get_total)) for item in order_items], Decimal("0.00"))

        if self.used_reward:
            total *= Decimal("0.90")

        total = total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return max(total, Decimal("0.00"))

    def get_total_nutrition(self):
        items = self.orderitem_set.all()

        total_nutrition = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}

        for item in items:
            if item.combo:  # Nếu đây là một combo
                for sub_item in item.combo.products.all():
                    total_nutrition["calories"] += sub_item.calories * item.quantity
                    total_nutrition["protein"] += sub_item.protein * item.quantity
                    total_nutrition["carbs"] += sub_item.carbs * item.quantity
                    total_nutrition["fat"] += sub_item.fat * item.quantity
            elif item.product:
                total_nutrition["calories"] += item.product.calories * item.quantity
                total_nutrition["protein"] += item.product.protein * item.quantity
                total_nutrition["carbs"] += item.product.carbs * item.quantity
                total_nutrition["fat"] += item.product.fat * item.quantity

        return total_nutrition

    @property
    def get_sale_discount_total(self):

        order_items = self.orderitem_set.all()
        total_discount = sum(
            [(Decimal(item.product.price) - Decimal(item.product.final_price)) * item.quantity for item in order_items
             if item.product and item.product.sale],
            Decimal("0.00")
        )
        return total_discount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @property
    def get_endow_discount_total(self):
        if self.used_reward:
            original_total = self.get_cart_total / Decimal("0.90")
            return (original_total * Decimal("0.10")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return Decimal("0.00")



class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    combo = models.ForeignKey(Combo, on_delete=models.SET_NULL, blank=True, null=True, related_name="order_items")
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=0, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        if self.combo:
            return self.combo.get_combo_price * self.quantity
        elif self.product:
            return self.product.final_price * self.quantity
        return 0

class MealPlan(models.Model):
    WEEKDAYS = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='meal_plans', null=True, blank=True)
    day = models.CharField(max_length=10, choices=WEEKDAYS)
    breakfast = models.ManyToManyField(Product, related_name='mealplan_breakfast', blank=True)
    lunch = models.ManyToManyField(Product, related_name='mealplan_lunch', blank=True)
    dinner = models.ManyToManyField(Product, related_name='mealplan_dinner', blank=True)
    snacks = models.ManyToManyField(Product, related_name='mealplan_snacks', blank=True)
    combos = models.ManyToManyField(Combo, related_name='mealplan_combos', blank=True)

    class Meta:
        unique_together = ('customer', 'day')

    def __str__(self):
        return f"Meal Plan for {self.customer.user.get_full_name()} - {self.day}"

    @property
    def total_nutrition(self):
        total = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
        all_products = list(self.breakfast.all()) + list(self.lunch.all()) + list(self.dinner.all()) + list(self.snacks.all())

        for product in all_products:
            total["calories"] += product.calories
            total["protein"] += product.protein
            total["carbs"] += product.carbs
            total["fat"] += product.fat

        for combo in self.combos.all():
            for item in combo.products.all():
                total["calories"] += item.calories
                total["protein"] += item.protein
                total["carbs"] += item.carbs
                total["fat"] += item.fat

        return total


class CustomerMessage(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="messages")
    message = models.TextField()
    nickname = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.nickname or 'Anonymous'} - {self.rating} ⭐ at {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    mobile = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address if self.address else "No Address"


class WeightTracking(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='weight_logs')
    date = models.DateField(default=now)
    height = models.FloatField()
    weight = models.FloatField()
    bmi = models.FloatField()
    health_status = models.CharField(max_length=50, default="Not rated yet")

    def __str__(self):
        return f"{self.customer.name} - {self.date} (BMI: {self.bmi})"

class GuestOrder(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='guest_order')
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(null=True)
    mobile = models.CharField(max_length=15, null=True)

    def __str__(self):
        return f"Guest Order for {self.name or 'Unknown'}"

