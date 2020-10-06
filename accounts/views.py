from django.shortcuts import render, redirect

from django.contrib.auth.models import User
from django.contrib.auth import login, logout

from .forms import CreateUserForm


def register(request):
    form = CreateUserForm()
    context = {'form': form}

    if request.method == 'POST':
        form = CreateUserForm(request.POST)

        if form.is_valid():
            email = request.POST.get('email')
            password = request.POST.get('password')
            email_split = email.split('@')
            user_name = email_split[0]

            new_user = User.objects.create_user(user_name, email, password)
            try:
                new_user.save()
                return redirect('blog:index')
            except Exception as e:
                context = {'form': form, 'error': e}

    return render(request, 'accounts/register.html', context)


def login_page(request):
    context = {}
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if email and password:
            email_split = email.split('@')
            if email_split:
                email_clear = email.strip()
                user = User.objects.get(email=email)
                if user is not None:
                    print('user not none ...')
                    login(request, user)
                    return redirect('blog:index')
                else:
                    print('user none ...')
                    error = 'Email or password incorrect 邮箱或密码不正确'
                    context = {'error': error}
        else:
            error = 'Email or password can not empty 邮箱或密码不能为空'
            context = {'error': error}

    return render(request, 'accounts/login.html', context)


def logout_page(request):
    logout(request)
    return redirect('accounts:login')
