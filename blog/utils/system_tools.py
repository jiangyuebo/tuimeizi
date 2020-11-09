import os

from blog.models import Poster, Media


# 查看文件夹占用磁盘信息
# folder 文件夹路径
def disk_stat(folder):
    hd = {}
    disk = os.statvfs(folder)
    print("disk: ", disk)
    # 剩余
    hd['free'] = disk.f_bavail * disk.f_frsize
    # 总共
    hd['total'] = disk.f_blocks * disk.f_frsize
    # 已使用
    hd['used'] = hd['total'] - hd['free']
    # 使用比例
    hd['used_proportion'] = float(hd['used']) / float(hd['total'])
    return hd


# 遍历媒体存储文件夹，删除垃圾文件（数据库中无记录文件夹）
def folder_clear():
    clear_result = {}
    scan_count = 0
    delete_count = 0
    recover_byte = 0
    # 获取工程路径
    project_path = os.getcwd()
    media_store_path = project_path + "/" + "media"
    # 遍历目录下所有子目录
    g = os.walk(media_store_path)
    for path, dir_list, file_list in g:
        if file_list:
            for file_name in file_list:
                scan_count += 1
                # 检查数数据库媒体，图片
                media_set = Media.objects.filter(local_url__endswith=file_name)
                if media_set:
                    # 有这个图片媒体文件, 判断是否有主
                    for media in media_set:
                        media_file_size = os.path.getsize(media.local_url)
                        is_deleted = judge_media_file_to_delete(media, "pic")
                        if is_deleted:
                            delete_count += 1
                            recover_byte = recover_byte + media_file_size
                else:
                    # 查询是否视频类型
                    media_video_set = Media.objects.filter(local_video_url__endswith=file_name)
                    if media_video_set:
                        # 判断此文件是否有主(poster)
                        for media in media_set:
                            media_file_size = os.path.getsize(media.local_video_url)
                            is_deleted = judge_media_file_to_delete(media, "video")
                            if is_deleted:
                                delete_count += 1
                                recover_byte = recover_byte + media_file_size
                    else:
                        # media 库中图片和视频分类均无，直接删除
                        media_path = path + "/" + file_name
                        media_file_size = os.path.getsize(media_path)
                        os.remove(media_path)
                        delete_count += 1
                        recover_byte = recover_byte + media_file_size

    clear_result['scan_count'] = scan_count
    clear_result['delete_count'] = delete_count
    clear_result['recover_byte'] = recover_byte
    return clear_result


# 判断媒体文件是否有主
def judge_media_file_to_delete(media, media_type):
    poster_id = media.user_id_str
    try:
        Poster.objects.get(user_id_str=poster_id)
        # has owner, do nothing
        return False
    except Exception as e:
        # cant find the poster, delete the media file
        if media_type == "video":
            media_local_path = media.local_video_url
        else:
            media_local_path = media.local_url
        os.remove(media_local_path)
        return True
