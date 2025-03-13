from django.contrib import messages
from django.contrib.auth import authenticate, login, logout,update_session_auth_hash
from app.models import *
from django.shortcuts import render, redirect


def register(request):
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            Customer.objects.create(user=user, name=user.username)

            messages.success(request, "Account created successfully!")
            return redirect('login')
        else:
            print("Form errors:", form.errors)
            messages.error(request, "Registration failed. Please check the form.")

    context = {'form': form}
    return render(request, 'app/login.html', context)


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        print(request.POST)
        identifier = request.POST.get('identifier')
        password = request.POST.get('password')
        if not identifier or not password:
            messages.error(request, 'Vui lòng nhập đầy đủ thông tin.')
            return render(request, 'app/login.html')

        username = None


        if '@' in identifier:  #
            try:
                user_obj = User.objects.get(email=identifier)
                username = user_obj.username
            except User.DoesNotExist:
                messages.error(request, 'Email không tồn tại.')
        else:
            username = identifier  #



        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Sai tên đăng nhập/email hoặc mật khẩu.')

    return render(request, 'app/login.html')

def logoutPage(request):
    logout(request)
    return redirect('home')

def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully!')
            return redirect('my_account')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ChangePasswordForm(user=request.user)

    return render(request, 'my_account.html', {'form': form})