import os, urllib.request
import traceback

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator

from .models import Post, Category, Tag, Poster, Media
from .utils import tweets_operator


# Create your views here.
# 首页列表
def index(request):
    # 读取poster数据
    poster_list = tweets_operator.load_target_posters()

    posters_covers_list_all = []
    if poster_list is not None and len(poster_list) > 0:
        # 根据poster查询他们的作品
        posters_covers_list_all = load_target_posters_cover(poster_list)

    posters_covers_list = []
    # 分页
    if posters_covers_list_all is not None and len(posters_covers_list_all) > 0:
        paginator = Paginator(posters_covers_list_all, 12)
        page = request.GET.get('page')
        posters_covers_list = paginator.get_page(page)

    return render(request, 'blog/index.html', context={
        'posters_covers_list': posters_covers_list,
    })


# 详细
def detail(request, user_id_str):
    # 将该poster浏览数+1
    poster = Poster.objects.get(user_id_str=user_id_str)
    poster.increase_views()
    # 获取该poster所有作品
    media_list_all = Media.objects.filter(user_id_str=user_id_str)
    # 分页
    media_list = []
    if len(media_list_all) > 0:
        paginator = Paginator(media_list_all, 12)
        page = request.GET.get('page')
        media_list = paginator.get_page(page)

    return render(request, 'blog/detail.html', context={'media_list': media_list})


# 查看大图
def enjoy(request, media_id_str):
    print('here is the enjoy function******')
    media = Media.objects.get(media_id_str=media_id_str)
    return render(request, 'blog/enjoy.html', context={'media': media})


# 归档列表
def archive(request, year, month):
    print('here is the archive function**********')
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
                cover_pic_list = Media.objects.filter(user_id_str=poster_id_str, is_cover=True)
                if len(cover_pic_list) > 0:
                    poster_cover_dic['cover'] = cover_pic_list[0]
                else:
                    cover_pic_list = Media.objects.filter(user_id_str=poster_id_str)
                    if len(cover_pic_list) > 0:
                        poster_cover_dic['cover'] = cover_pic_list[0]
                    else:
                        print('无该poster作品 : ', poster.user_screen_name)
                        continue
            except Exception as e:
                print('error :', e)

            posters_covers_list.append(poster_cover_dic)

        return posters_covers_list
    else:
        print('poster_list is none or empty')
