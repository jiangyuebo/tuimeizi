from django.core.management import BaseCommand

from blog.utils import tweets_operator


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('*** *** 启动 timer 工作任务 *** ***')
        tweets_operator.timer_operation()
