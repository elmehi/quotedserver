from __future__ import unicode_literals

from django.db import models
import datetime

# A source model.
class Source(models.Model):
    source_quote = models.TextField()
    source_url = models.CharField(max_length = 200)
    source_title = models.CharField(max_length = 200)
    source_name = models.CharField(max_length = 200)
    source_date = models.DateTimeField(default=datetime.date.today)

    def __str__(self):
         return self.source_quote
