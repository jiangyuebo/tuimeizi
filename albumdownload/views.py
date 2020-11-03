from django.shortcuts import render
from django.core.paginator import Paginator

from .models import Album, AlbumPic, AlbumDownloadPath


# Create your views here.
def album_index(request):
    # 专辑与专辑封面对应数组
    title_cover_list = []
    # 获取专辑信息
    album_list = Album.objects.all().order_by("-create_date")
    for album in album_list:
        title_cover_dic = {'album_id': str(album.id), 'title': album.title}
        # 查询封面图片
        album_cover = AlbumPic.objects.filter(album=album, is_cover=True)[0]
        if album_cover:
            title_cover_dic['cover'] = album_cover
        else:
            album_cover = AlbumPic.objects.filter(album=album)[0]
            title_cover_dic['cover'] = album_cover

        title_cover_list.append(title_cover_dic)

    # 分页
    media_list = []
    if len(title_cover_list) > 0:
        paginator = Paginator(title_cover_list, 10)
        page = request.GET.get('page')
        media_list = paginator.get_page(page)

    return render(request, "albumdownload/album.html", context={
        'album_list': media_list,
    })


def album_detail(request, album_id):
    # 专辑信息
    album = Album.objects.get(id=album_id)
    # 预览图信息
    album_pics = AlbumPic.objects.filter(album=album)
    # 获取下载信息
    album_download_paths = AlbumDownloadPath.objects.filter(album=album)

    return render(request, "albumdownload/album_detail.html", context={
        'album': album,
        'album_pics': album_pics,
        'album_download_paths': album_download_paths,
    })



