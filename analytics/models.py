from django.db import models

from .utils import get_client_ip


# Create your models here.
class ObjectViewed(models.Model):
    user_id = models.TextField(max_length=100, null=True, blank=True)
    url = models.TextField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.CharField(max_length=220, blank=True, null=True)

    def __str__(self):
        return "%s viewed on %s at ip: %s" % (self.url, self.timestamp, self.ip_address)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Object viewed'


def count(user_id, url, request):
    new_viewed_object = ObjectViewed.objects.create(
        user_id=user_id,
        url=url,
        ip_address=get_client_ip(request)
    )









