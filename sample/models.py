from datetime import datetime
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models
from jsonfield import JSONField


class Product(models.Model):
    site = models.ForeignKey(Site)
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    price = models.FloatField()
    priority = models.IntegerField(default=100)
    description = models.TextField(null=True)
    thumbnail = models.CharField(max_length=200, null=True)
    picture = models.CharField(max_length=200, null=True)
    on_site = CurrentSiteManager()

    class Meta:
        ordering = ('priority', 'name')


class Sample(models.Model):
    user_ref = models.CharField(max_length=50, db_index=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    purchased = models.BooleanField(default=False, db_index=True)
    processed = models.BooleanField(default=False, db_index=True)
    created = models.DateTimeField(default=datetime.now)
    sample_data = JSONField()

    class Meta:
        ordering = ('created', )