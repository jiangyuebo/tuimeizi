from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages

from .models import Post, Category, Tag, Poster, Media
from .utils import tweets_operator
from analytics import models

from accounts.models import Favorite


# Create your views here.
# 首页列表
def index(request):
    models.count('', 'index', request)

    # 读取poster数据
    poster_list = tweets_operator.load_target_posters()

    posters_covers_list_all = []
    if poster_list is not None and len(poster_list) > 0:
        # 根据poster查询他们的作品
        posters_covers_list_all = load_target_posters_cover(poster_list)

    posters_covers_list = []
    page_round = []
    # 分页
    if posters_covers_list_all is not None and len(posters_covers_list_all) > 0:
        paginator = Paginator(posters_covers_list_all, 12)
        page = request.GET.get('page')
        posters_covers_list = paginator.get_page(page)
        page_round = getRoundPage(page, paginator)

    return render(request, 'blog/index.html', context={
        'posters_covers_list': posters_covers_list,
        'page_round': page_round
    })


# 详细
def detail(request, user_id_str):
    models.count('', 'detail', request)
    # 将该poster浏览数+1
    poster = Poster.objects.get(user_id_str=user_id_str)
    poster.increase_views()
    # 获取该poster所有作品
    media_list_all = Media.objects.filter(user_id_str=user_id_str).order_by("-id")
    # 获取该poster显示名
    poster_user_name = poster.user_name
    # 分页
    media_list = []
    page_round = []
    if len(media_list_all) > 0:
        paginator = Paginator(media_list_all, 12)
        page = request.GET.get('page', 1)
        media_list = paginator.get_page(page)
        page_round = getRoundPage(page, paginator)

    return render(request, 'blog/detail.html', context={
        'media_list': media_list,
        'user_name': poster_user_name,
        'page_round': page_round
    })


def getRoundPage(current_num, paginator):
    # 大于11页时
    if paginator.num_pages > 11:
        # 当前页码的后5页数超过最大页码时，显示最后10项
        if int(current_num) + 5 > paginator.num_pages:
            page_range = range(paginator.num_pages - 10, paginator.num_pages + 1)
        # 当前页码的前5页数为负数时，显示开始的10项
        elif int(current_num) - 5 < 1:
            page_range = range(1, 12)
        else:
            # 显示左5页到右5页的页码
            page_range = range(int(current_num) - 5, int(current_num) + 5 + 1)
    # 小于11页时显示所有页码
    else:
        page_range = paginator.page_range

    return page_range


# 查看大图
def enjoy(request, media_id_str):
    models.count('', 'enjoy', request)

    # 获取media数据
    try:
        media = Media.objects.get(media_id_str=media_id_str)

        post_text_origin = media.post_text
        # split 去掉文字后面的链接
        str_list = post_text_origin.split("https")
        media.post_text = str_list[0]

        # 获取poster数据
        poster = Poster.objects.get(user_id_str=media.user_id_str)
        # get favorite data
        try:
            Favorite.objects.get(favorite_media_id=media_id_str, favorite_user=request.user)
            favorite_class = 'btn-success'
            favorite_text = '已收藏'
        except Exception as e:
            favorite_class = 'btn-danger'
            favorite_text = '收藏'
        return render(request, 'blog/enjoy.html', context={
            'enjoy_content': media, 'poster': poster, 'favorite_class': favorite_class, 'favorite_text': favorite_text
        })
    except Exception as e:
        return render(request, 'blog/error.html', context={
            'error_title': '哎哟！',
            'error_content': '该图片已经被删除了！每次更新后系统会删除无用图片及视频，请重新进入相关妹子继续使用。谢谢！'
        })


# 归档列表
def archive(request, year, month):
    post_list = Post.objects.filter(created_time__year=year,
                                    created_time__month=month
                                    ).order_by('-created_time')
    return render(request, 'blog/index.html', context={'post_list': post_list})


# 分类页
def category(request, pk):
    cate = get_object_or_404(Category, pk=pk)
    post_list = Post.objects.filter(category=cate).order_by('-created_time')
    return render(request, 'blog/index.html', context={'post_list': post_list})


# 标签页
def tag(request, pk):
    t = get_object_or_404(Tag, pk=pk)
    post_list = Post.objects.filter(tags=t).order_by('-created_time')
    return render(request, 'blog/index.html', context={'post_list': post_list})


def search(request):
    q = request.GET.get('q')
    if not q:
        error_msg = '请输入搜索关键字'
        messages.add_message(request, messages.ERROR, error_msg, extra_tags='danger')
        return redirect('blog:index')

    # 读取poster数据
    poster_list = tweets_operator.load_target_posters(q)

    posters_covers_list_all = []
    if poster_list is not None and len(poster_list) > 0:
        # 根据poster查询他们的作品
        posters_covers_list_all = load_target_posters_cover(poster_list)

    return render(request, 'blog/index.html', context={
        'posters_covers_list': posters_covers_list_all,
    })


# 获取目标用户封面
def load_target_posters_cover(poster_list):
    if poster_list is not None and len(poster_list) > 0:
        # poster与cover对应的数组
        posters_covers_list = []

        for poster in poster_list:
            poster_id_str = poster.user_id_str
            poster_cover_dic = {'poster': poster}
            # 获取poster作品封面，如果未定义封面责取第一张作品为封面
            try:
                # 获取设定为封面的media
                cover_pic_list = Media.objects.filter(user_id_str=poster_id_str, is_cover=True)

                if len(cover_pic_list) > 0:
                    cover_media = cover_pic_list[0]
                    # 获取时间排序最新的media
                    poster_media_list = Media.objects.order_by('-created_at').filter(user_id_str=poster_id_str)
                    latest_media = poster_media_list[0]
                    # 设置最新更新日期
                    cover_media.created_at = latest_media.created_at
                    # 设置封面图片
                    poster_cover_dic['cover'] = cover_media
                else:
                    cover_pic_list = Media.objects.filter(user_id_str=poster_id_str)
                    if len(cover_pic_list) > 0:
                        poster_cover_dic['cover'] = cover_pic_list[0]
                    else:
                        continue
            except Exception as e:
                pass

            posters_covers_list.append(poster_cover_dic)

        # 根据更新时间进行排序
        posters_covers_list.sort(key=lambda r: r['cover'].created_at, reverse=True)
        return posters_covers_list


def favorite(request):
    if request.user.is_authenticated:
        # 获取该用户收藏媒体对象
        favorite_list_all = Favorite.objects.filter(favorite_user=request.user).order_by("-create_date")
        # 获取收藏媒体
        favorite_media_list = []
        for favorite_item in favorite_list_all:
            media_id_str = favorite_item.favorite_media_id
            # 判断收藏内容还是否存在
            if media_id_str:
                media = Media.objects.filter(media_id_str=media_id_str)[0]
                favorite_media_list.append(media)
            else:
                continue

        # 分页
        media_list = []
        if len(favorite_media_list) > 0:
            paginator = Paginator(favorite_media_list, 10)
            page = request.GET.get('page')
            media_list = paginator.get_page(page)

        return render(request, 'blog/favorite.html', context={
            'media_list': media_list
        })
    else:
        return render(request, 'accounts/login.html')