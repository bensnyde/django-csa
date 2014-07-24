from django.contrib import admin
from .models import Category, Tag, Article

admin.site.register(Article)
admin.site.register(Tag)
admin.site.register(Category)
