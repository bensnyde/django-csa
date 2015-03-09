from django.forms import ModelForm
from .models import Category, Article, Tag

class CategoryForm(ModelForm):
	class Meta:
		model = Category
		exclude = ['changed_by']

class TagForm(ModelForm):
	class Meta:
		model = Tag
		exclude = ['changed_by']

class ArticleForm(ModelForm):
	class Meta:
		model = Article
		exclude = ['author', 'modified', 'changed_by']