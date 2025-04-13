from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import RegisterForm, LoginForm
from django.contrib.auth.decorators import login_required
from .decorators import site_admin_required


#@login_required
def palace_base_view(request):
    return render(request, 'palace/home.html')


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  # Здесь мы сохраняем пользователя
            login(request, user)  # Здесь мы логиним пользователя
            return redirect('palace_base')  #
    else:
        form = RegisterForm()
    return render(request, 'account/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('palace_base')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('palace_base')


@site_admin_required
def admin_dashboard(request):
    # Ваш код для админ-панели сайта
    return render(request, 'account/admin_dashboard.html')
