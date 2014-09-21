from django.forms import ModelForm
from .models import Category, Article, Tag

class CategoryForm(ModelForm):
	class Meta:
		model = Category

class TagForm(ModelForm):
	class Meta:
		model = Tag

class ArticleForm(ModelForm):
	class Meta:
		model = Article
		fields = ['title', 'contents', 'category', 'tags']