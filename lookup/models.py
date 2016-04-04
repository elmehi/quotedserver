from __future__ import unicode_literals

from django.db import models

# A source model.
class Source(models.Model):
    quote = models.TextField()
    url = models.CharField(max_length = 200)
    title = models.CharField(max_length = 200)
    # author = models.CharField(max_length = 200)
    name = models.CharField(max_length = 200)
    # date = models.DateTimeField(auto_now=False, auto_now_add=False)

    def __str__(self):
        return self.quote
