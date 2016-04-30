from __future__ import unicode_literals
import django
from django.db import models
from django.contrib.postgres import fields
import datetime

class SecondarySource(models.Model):
    source_url = models.TextField()
    article_title = models.TextField()
    
    def __str__(self):
        return self.article_title

# A source model.
class Source(models.Model):
    source_quote = models.TextField()
    source_url = models.TextField()
    source_title = models.TextField()
    source_name = models.TextField()
    source_date = models.DateTimeField(default=django.utils.timezone.now)
    other_matches = fields.ArrayField(models.ForeignKey(SecondarySource, on_delete=models.CASCADE), blank=True, default=list)
    
    def __str__(self):
        return self.source_quote

class User(models.Model):
    highlighting_state = models.IntegerField(default=2)
    username = models.TextField()
    password = models.TextField()
    highlight_url = models.BooleanField(default = True)
    date_created = models.DateTimeField(default=django.utils.timezone.now)
    domains = fields.ArrayField(models.CharField(max_length=200), blank=True, default=list)
    trusted_sources = fields.ArrayField(models.CharField(max_length=200), blank=True, default=list)
    untrusted_sources = fields.ArrayField(models.CharField(max_length=200), blank=True, default=list)
    
    def __str__(self):
        return self.username

class Request(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    request_date = models.DateTimeField(default=django.utils.timezone.now)
    request_source = models.ForeignKey(Source, on_delete=models.DO_NOTHING)
