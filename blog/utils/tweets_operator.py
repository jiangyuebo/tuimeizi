import datetime
import os
import time
import urllib.request
from threading import Timer
from PIL import Image, ImageChops

import tweepy
import dhash

from blog.models import MediaDHashRecord


from blog.models import Poster, Media, DeletedMedia
from blog.utils import system_tools

one_fetch_tweets_count = 200


def setup_poster_and_fetch_tweets(screen_name, category):
    poster = install_poster_into_database(screen_name, category)
    fetch_all_tweets_from_poster(poster)


# tweepy init
def init_my_tweepy():
    auth = tweepy.OAuthHandler('mUAXhVuRst8HCFUrwXhhY268y',
                               'xkD9RfnCZLizOEVBXT6MxGHBQ6ADBQDd2cFpIrQeuobKwGrXJz')
    auth.set_access_token("273242373-TZGgTaBVAYt4n9Cah8qy4tMLHjGZ0Nsx91F8XXBZ",
                          'Sib2WGUfQsyn9o26uA9W1dImtHtgTFlk3SHOTZZiA0oQ1')
    api = tweepy.API(auth)
    return api


# 插入poster 参数：screen_name(poster名)/category_id(分类ID)
def install_poster_into_database(screen_name, category):
    api = init_my_tweepy()
    poster = fetch_twitter_poster_info_by_screen_name(api, screen_name)

    if poster is not None:
        # set poster's category
        poster.category = category
        # save poster info
        save_poster_data_into_database(poster)
        return poster


# 通过screen name获取twitter用户信息
def fetch_twitter_poster_info_by_screen_name(api, user_screen_name):
    if api is not None:
        poster_info = api.get_user(user_screen_name)
        if poster_info is not None:
            poster_info_dic = poster_info._json
            # 获取poster数据
            id_str = poster_info_dic['id_str']
            name = poster_info_dic['name']
            screen_name = poster_info_dic['screen_name']

            poster = Poster(user_id_str=id_str, user_screen_name=screen_name, user_name=name)
            return poster


# 存储poster数据到数据库
def save_poster_data_into_database(poster):
    if poster is not None:
        # 检查是否已存在
        try:
            Poster.objects.get(user_id_str=poster.user_id_str)
        except Poster.DoesNotExist:
            poster.save()


# 获取目标用户组 可选参数：poster中文名
def load_target_posters(poster_screen_name=''):
    try:
        if poster_screen_name:
            poster_list = Poster.objects.filter(user_screen_name=poster_screen_name)
        else:
            poster_list = Poster.objects.order_by("created_time")
        return poster_list
    except Poster.DoesNotExist:
        print('无目标 poster 存在')


# 抓取并存储所有目标poster的推文
def fetch_tweets_data_from_target_posters():
    api = init_my_tweepy()
    poster_list = load_target_posters()

    if api is not None and poster_list is not None and len(poster_list) > 0:
        fetch_tweets_from_posters(api, poster_list)


def fetch_tweets_data_from_target_posters_in_index(start_index, end_index):
    api = init_my_tweepy()
    poster_list = load_target_posters()
    if api is not None and poster_list is not None and len(poster_list) > 0:
        if (len(poster_list)-1) < end_index:
            end_index = len(poster_list)-1
        fetch_list = poster_list[start_index:end_index]
        fetch_tweets_from_posters(api, fetch_list)


def fetch_tweets_from_posters(api, fetch_posters_list):
    if fetch_posters_list is not None and len(fetch_posters_list) > 0:
        for poster in fetch_posters_list:
            # 判断当前poster是否已经获取过推文
            exsist_tweets = Media.objects.filter(user_id_str=poster.user_id_str)
            if len(exsist_tweets) > 0:
                # 已获取过推
                fetch_latest_tweets_from_poster(api, exsist_tweets, poster)
            else:
                # 未获取过
                fetch_all_tweets_from_poster(poster)


# 获取指定poster全量推文
def fetch_all_tweets_from_poster(poster):
    api = init_my_tweepy()

    all_tweets = []
    new_tweets = api.user_timeline(screen_name=poster.user_screen_name, count=one_fetch_tweets_count)
    # 缓存推文
    all_tweets.extend(new_tweets)
    # 保存最老推文ID
    oldest = get_the_oldest_tweet_id(all_tweets)
    while len(new_tweets) > 0:
        is_finished = 0
        while is_finished == 0:
            try:
                new_tweets = api.user_timeline(screen_name=poster.user_screen_name,
                                               count=one_fetch_tweets_count, max_id=oldest)
                is_finished = 1
            except Exception as e:
                print(e)
                is_finished = 1
        # save
        all_tweets.extend(new_tweets)
        oldest = get_the_oldest_tweet_id(all_tweets)

    # 处理返回推文
    tweetsOperator(all_tweets)


# 获取最新推文
def fetch_latest_tweets_from_poster(api, exsist_tweets, poster):
    latest_post_id = exsist_tweets[0].post_id_str

    all_tweets = []
    flag = True
    while flag:
        is_finished = 0
        new_tweets = []
        while is_finished == 0:
            try:
                # 老poster使用ID获取数据，解决screen_name 频繁变更问题
                new_tweets = api.user_timeline(id=poster.user_id_str,
                                               count=one_fetch_tweets_count, since_id=latest_post_id)
                is_finished = 1
                if len(new_tweets) > 0:
                    flag = True
                else:
                    flag = False
            except Exception as e:
                is_finished = 1
                flag = False
                print('---> error poster:%s' % poster.user_screen_name)
                print(e)
                break

        # save
        if new_tweets is not None and len(new_tweets) > 0:
            if all_tweets is not None and len(all_tweets) > 0:
                all_tweets = new_tweets.extend(all_tweets)
                tweet = all_tweets[0]
                latest_post_id = tweet.id + 1
            else:
                all_tweets = new_tweets
                tweet = all_tweets[0]
                latest_post_id = tweet.id + 1

    if len(all_tweets) > 0:
        # 处理返回推文
        tweetsOperator(all_tweets)


# 获取最老推文ID
def get_the_oldest_tweet_id(all_tweets):
    return all_tweets[-1].id - 1


# 推文数据处理方法
# statusData tweepy获取到的数据集合
def tweetsOperator(statusDatas):
    index = 0
    if len(statusDatas) > 0:
        for status in statusDatas:
            status_json_dic = status._json

            # 获取用户及推文信息
            # 创建时间
            created_at = status_json_dic['created_at']
            # python date
            created_at_python_date = transform_twitter_date_to_python_date(created_at)
            # 推文ID
            post_id_str = status_json_dic['id_str']
            # 推文文字
            post_text = status_json_dic['text']

            user_info_dic = status_json_dic['user']
            user_id_str = user_info_dic['id_str']
            user_screen_name = user_info_dic['screen_name']

            # 判断不是转推
            if 'retweeted_status' not in status_json_dic:
                # 判断字典中是否有extended_entities字段，有的话说明有多个媒体文件
                if 'extended_entities' in status_json_dic:
                    # 获取媒体字段
                    extended_entities_dic = status_json_dic['extended_entities']
                    media_list = extended_entities_dic['media']

                    for media in media_list:
                        media_id_str = media['id_str']
                        media_type = media['type']
                        media_url = media['media_url']

                        # 如果媒体已在删除列表中记录，跳过不进行下载
                        deleted_media_record = DeletedMedia.objects.filter(post_id_str=post_id_str, media_id_str=media_id_str)
                        if deleted_media_record:
                            # 如果有记录，此媒体不进行保存，跳到下一个
                            continue

                        # 图片名称
                        photo_file_name = os.path.basename(media_url)
                        # 获取存储全路径
                        dest_file_full_path = get_file_local_full_path(user_screen_name, photo_file_name)

                        media_data = Media(
                            user_id_str=user_id_str,
                            post_id_str=post_id_str,
                            post_text=post_text,
                            media_id_str=media_id_str,
                            media_type=media_type,
                            remote_url=media_url,
                            created_at=created_at_python_date,
                            local_url=dest_file_full_path,
                            is_cover=False
                        )

                        save_media_data_into_database(media_data)
                        # 获取文件夹路径
                        dest_dev_path = get_poster_local_store_dev_path(user_screen_name)
                        # 存储图片
                        download_file_from_url(media_data, dest_dev_path, dest_file_full_path, media_url)

                        if media_type == 'video':
                            video_info_list = media['video_info']['variants']
                            bitrate_temp = 0
                            best_video_url = ""

                            # 获取最高清视频地址
                            for video_info in video_info_list:
                                if 'bitrate' in video_info:
                                    bitrate = video_info['bitrate']
                                    if bitrate > bitrate_temp:
                                        bitrate_temp = bitrate
                                        best_video_url = video_info['url']

                            video_file_name_str = os.path.basename(best_video_url)
                            if '?' in video_file_name_str:
                                video_file_name = video_file_name_str.split("?")[0]
                            else:
                                video_file_name = video_file_name_str

                            # 下载视频
                            if len(video_file_name) > 0:
                                http_video_url = best_video_url.replace("https", "http")
                                dest_video_full_path = get_file_local_full_path(user_screen_name, video_file_name)

                                # 存储视频媒体数据到数据库
                                media_just_saved = load_media_data_from_database(media_data)
                                if media_just_saved is not None:
                                    media_just_saved.local_video_url = dest_video_full_path
                                    media_just_saved.save()

                                # 下载视频媒体文件
                                download_file_from_url(media_data, dest_dev_path, dest_video_full_path, http_video_url)

            index = index + 1


# 转换twitter date 成 python date
def transform_twitter_date_to_python_date(twitter_date):
    if twitter_date is not None and len(twitter_date) > 0:
        ts = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(twitter_date, '%a %b %d %H:%M:%S +0000 %Y'))
        # 获取年月日
        year_str = time.strftime('%Y', time.strptime(twitter_date, '%a %b %d %H:%M:%S +0000 %Y'))
        month_str = time.strftime('%m', time.strptime(twitter_date, '%a %b %d %H:%M:%S +0000 %Y'))
        day_str = time.strftime('%d', time.strptime(twitter_date, '%a %b %d %H:%M:%S +0000 %Y'))
        # 创建 python date
        python_date = datetime.date(int(year_str), int(month_str), int(day_str))
        return python_date


# 获取文件本地存储全路径
def get_file_local_full_path(poster_screen_name, file_name):
    dest_dev = get_poster_local_store_dev_path(poster_screen_name)
    # 文件全路径
    media_local_full_path = os.path.join(dest_dev, file_name)
    return media_local_full_path


# 获取目标poster本地存储文件夹路径
def get_poster_local_store_dev_path(poster_screen_name):
    # 获取工程路径
    project_path = os.getcwd()
    # 判断磁盘空间
    media_store_path = project_path + "/" + "media/"
    # 计算可用空间
    # local_media_disk_free_size = get_free_space_size(media_store_path)
    # if local_media_disk_free_size < 10240:
    #     media_store_path = project_path + "/" + "media/mnt/"
    # 存储文件夹路径
    destination_dev = media_store_path + poster_screen_name
    return destination_dev


# 计算文件夹可用可用空间
def get_free_space_size(path):
    info = os.statvfs(path)
    free_size = info.f_frsize * info.f_bavail / 1024 / 1024
    return free_size


# 存储media数据到数据库
def save_media_data_into_database(media):
    if media is not None:
        # 检查是否已存在
        try:
            Media.objects.get(media_id_str=media.media_id_str)
        except Media.DoesNotExist:
            media.save()


# 下载文件到本地
# 数据对象/用户名/文件名/下载URL
def download_file_from_url(media_item, store_dev, store_full_path, url):
    try:
        # 判断文件夹是否存在，不存在责创建
        if not os.path.exists(store_dev):
            os.makedirs(store_dev)
        # 判断文件是否存在
        if not os.path.isfile(store_full_path):
            # 不存在，下载
            result = urllib.request.urlretrieve(url, store_full_path)
            if result:
                # 下载结束，加水印
                # 判断是否图片
                if store_full_path.lower().endswith(('.bmp', '.dib', '.png', '.jpg', '.jpeg', '.pbm', '.pgm', '.ppm', '.tif', '.tiff')):
                    # 打水印前计算D Hash
                    d_hash_of_image = d_hash_of_the_image(store_full_path)
                    d_hash_str = str(d_hash_of_image)
                    # 判断hash记录中是否已存在该图片
                    try:
                        MediaDHashRecord.objects.get(d_hash=d_hash_str)
                        # 已存在，删除图片
                        # 记录删除媒体
                        deleted_media_record = DeletedMedia(post_id_str=media_item.post_id_str,
                                                            media_id_str=media_item.media_id_str)
                        deleted_media_record.save()
                        # 删除数据
                        # 删除文件
                        delete_local_file_by_path(store_full_path)
                        if media_item.id:
                            # id 有值，正常删除
                            media_item.delete()
                        else:
                            # id 为None，根据path删除
                            delete_media_list = Media.objects.filter(local_url=store_full_path)
                            for delete_media in delete_media_list:
                                delete_media.delete()

                    except MediaDHashRecord.DoesNotExist:
                        # 不存在，保留媒体，并记录hash
                        media_d_hash_record = MediaDHashRecord(
                            d_hash=d_hash_str
                        )
                        media_d_hash_record.save()
                        # 打水印
                        system_tools.image_add_water_mark(store_full_path)
    except Exception as e:
        print('download_file_from_url error :', e)


# 计算图片的 d hash
def d_hash_of_the_image(image_path):
    the_image = Image.open(image_path)
    try:
        row, col = dhash.dhash_row_col(the_image)
        the_d_hash = dhash.format_hex(row, col)
        return the_d_hash
    except OSError:
        pass


# 删除本地文件
def delete_local_file_by_path(file_local__path):
    if os.path.exists(file_local__path):
        # 文件存在
        try:
            os.remove(file_local__path)
        except Exception as e:
            print(e)


# 读取media数据
def load_media_data_from_database(media):
    if media is not None:
        try:
            media_selected = Media.objects.get(post_id_str=media.post_id_str)
            return media_selected
        except Media.DoesNotExist:
            print('media post id(%s) 不存在' % media.post_id_str)


def timer_operation():
    fetch_tweets_data_from_target_posters()
    s_timer = Timer(60 * 60 * 12, timer_operation)
    s_timer.start()
