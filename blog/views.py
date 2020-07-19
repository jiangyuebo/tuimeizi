from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages

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
    # 获取该poster显示名
    poster_user_name = poster.user_name
    # 分页
    media_list = []
    if len(media_list_all) > 0:
        paginator = Paginator(media_list_all, 12)
        page = request.GET.get('page')
        media_list = paginator.get_page(page)

    return render(request, 'blog/detail.html', context={
        'media_list': media_list,
        'user_name': poster_user_name
    })


# 查看大图
def enjoy(request, media_id_str):
    media = Media.objects.get(media_id_str=media_id_str)
    return render(request, 'blog/enjoy.html', context={'enjoy_content': media})


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
                print(e)

            posters_covers_list.append(poster_cover_dic)

        # 根据更新时间进行排序
        posters_covers_list.sort(key=lambda r: r['cover'].created_at, reverse=True)
        return posters_covers_list
