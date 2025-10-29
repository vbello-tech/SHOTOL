from django.contrib import admin
from .models import URL, UrlHistory

# Register your models here.


admin.site.register(URL)
admin.site.register(UrlHistory)
