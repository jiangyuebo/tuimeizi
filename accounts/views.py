from django.shortcuts import render, redirect, reverse

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.db.models import Q

from .forms import UserRegisterForm, UserLoginForm
from .models import UserInformation

from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url

import json


def register(request):
    if request.method == 'GET':
        user_register_form = UserRegisterForm()
        return render(request, 'accounts/register.html', {
            'form': user_register_form
        })
    else:
        # POST
        user_register_form = UserRegisterForm(request.POST)
        if user_register_form.is_valid():
            email = user_register_form.cleaned_data['email']
            password = user_register_form.cleaned_data['password']

            user_list = User.objects.filter(Q(username=email) | Q(email=email))
            if user_list:
                return render(request, 'accounts/register.html', {
                    'error': '用户已经存在'
                })
            else:
                new_user = User.objects.create_user(email, email, password)
                new_user.save()
                user_saved = User.objects.get(email=email)
                # create user information model
                if user_saved:
                    user_information = UserInformation(information_user=user_saved)
                    user_information.save()
                    login(request, new_user)
                    return redirect(reverse('blog:index'))
                else:
                    return render(request, 'accounts/register.html', {
                        'error': '注册失败，原因未知'
                    })
        else:
            return render(request, 'accounts/register.html', {
                    'form': user_register_form
                })


def login_page(request):

    if request.method == 'GET':
        return render(request, 'accounts/login.html')
    else:
        user_login_form = UserLoginForm(request.POST)
        if user_login_form.is_valid():
            email = user_login_form.cleaned_data['email']
            password = user_login_form.cleaned_data['password']

            user = authenticate(username=email, password=password)
            if user:
                login(request, user)
                return redirect(reverse('blog:index'))
            else:
                return render(request, 'accounts/login.html', {
                    'error': '邮箱或密码不正确'
                })
        else:
            return render(request, 'accounts/login.html', {
                'form': user_login_form
            })


def logout_page(request):
    logout(request)
    return redirect('accounts:login')


# generate the captcha
def captcha():
    hash_key = CaptchaStore.generate_key()
    image_url = captcha_image_url(hash_key)
    captcha = {'hash_key': hash_key, 'image_url': image_url}
    return captcha


# refresh the captcha
def refresh_captcha(request):
    return HttpResponse(json.dumps(captcha()), content_type='application/json')


def verify_captcha(captcha_str, captcha_hash_key):
    if captcha_str and captcha_hash_key:
        try:
            get_captcha = CaptchaStore.objects.get(hashkey=captcha_hash_key)
            if get_captcha.response == captcha_str.lower():
                return True
        except:
            return False
    else:
        return False
