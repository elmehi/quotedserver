from django.contrib import admin
from models import Source, User, Request, Metadata

# Register your models here.
admin.site.register(Source)
admin.site.register(User)
admin.site.register(Request)
admin.site.register(Metadata)