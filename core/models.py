from django.db import models
from . import managers


class TimeStampedModel(models.Model):
    """ Time Stamped Model """
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    objects = managers.CustomModelManager()

    class Meta:
        abstract = True # 데이터베이스에 나타나지 않는 모델을 설정하는 법(추상모델)