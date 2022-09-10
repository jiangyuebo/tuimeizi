from django.shortcuts import render, redirect, reverse

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.db.models.aggregates import Count
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .forms import UserRegisterForm, UserLoginForm
from .models import UserInformation, Favorite


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


@csrf_exempt
def add_favorite(request):
    # determine whether user is logged or not
    if request.user.is_authenticated:
        # login
        # check the favorite count
        favorite_count = Favorite.objects.filter(favorite_user=request.user).count()
        if favorite_count < 10000000000:
            # favorite less than 10
            media_id_str = request.POST["media_id_str"]
            operation = save_favorite_media(request.user, media_id_str)
            return JsonResponse({'result': operation}, status=200)
        else:
            # favorite more than 10, check user active status
            user_information = UserInformation.objects.filter(information_user=request.user)[0]
            if user_information.is_active:
                # user is active, save the pic
                media_id_str = request.POST["media_id_str"]
                operation = save_favorite_media(request.user, media_id_str)
                return JsonResponse({'result': operation}, status=200)
            else:
                # user is not active, can't save the pic
                return JsonResponse({'result': 'refuse', 'message': '因服务器空间原因，只能收藏10个'}, status=200)
    else:
        # not logged in, redirect to login page
        return JsonResponse({'result': 'needLogin'}, status=200)


def save_favorite_media(user, media_id_str):
    try:
        favorite = Favorite.objects.get(favorite_user=user, favorite_media_id=media_id_str)
        # favorite exist, it's delete operation
        favorite.delete()
        return 'delete'
    except Exception as e:
        # favorite not exist, create it
        new_favorite = Favorite(favorite_user=user, favorite_media_id=media_id_str)
        new_favorite.save()
        return 'add'


def delete_favorite(request, media_id_str):
    if request.user.is_authenticated:
        favorite_media = Favorite.objects.filter(favorite_user=request.user, favorite_media_id=media_id_str)
        if favorite_media:
            # exist, delete it
            favorite_media.delete()
        else:
            pass
        return JsonResponse({'result': 'success'}, status=200)
    else:
        pass
