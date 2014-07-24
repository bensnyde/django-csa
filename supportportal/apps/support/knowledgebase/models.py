from django.db import models
from django.conf import settings
from datetime import datetime
from django.forms.models import model_to_dict
from django.template import defaultfilters

class Category(models.Model):
    title = models.SlugField(max_length=64, null=False, blank=False, unique=True)

    def __unicode__(self):
        return '%s' % (self.title)
   

class Tag(models.Model):
    title = models.SlugField(max_length=64, null=False, blank=False, unique=True)

    def __unicode__(self):
        return '%s' % (self.title)
        

class Article(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, blank=False, related_name="knowledgebase_author")
    title = models.SlugField(max_length=128, blank=False, null=False)
    contents = models.TextField(blank=False, null=False)
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()
    views = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, blank=False, null=False)
    tags = models.ManyToManyField(Tag)

    def __unicode__(self):
        return '%s' % (self.title)

    def save(self, *args, **kwargs):
            ''' On save, update timestamps '''
            if not self.id:
                    self.created = datetime.today()
            self.modified = datetime.today()
            super(Article, self).save(*args, **kwargs)

    def dump_to_dict(self):
    	tags = []
    	for tag in self.tags.all():
    		tags.append({"id": tag.pk, "title": tag.title})

        return {
            "id": self.pk,
        	"author": self.author.get_full_name(),
        	"title": self.title,
        	"views": self.views,
        	"category": self.category.title,
        	"created": defaultfilters.date(self.created, "SHORT_DATETIME_FORMAT"),
        	"modified": defaultfilters.date(self.modified, "SHORT_DATETIME_FORMAT"),
        	"contents": self.contents,
        	"tags": tags
        }

def get_categories_annotate_articles():
    """Get Categories annotated with Articles

        Retrieves list of categories annotated with their associated articles.

    Parameters
        None
    Returns
        kb_categories: queryset of Categories and Articles
            [{"category": "Category 1", "articles": [<Article 1>, <Article 2>]}]
    """    
    kb_categories = []
    for category in Category.objects.annotate(count=models.Count('article')):
        articles_list = []
        for article in Article.objects.filter(category=category.id):
            articles_list.append({"id": article.pk, "author": article.author.get_full_name(), "title": article.title, "views": article.views, "category": article.category.title, "updated": str(article.modified)})

        kb_categories.append({
            "category": category.title, 
            "articles": articles_list
        })  

    return kb_categories          

def increment_articles_views(article_id):
    """Increment Article views 

        Increments view count on specified Article.

    Parameters
        article_id: int article id
    Returns
        bool result
    """    
    return Article.objects.filter(pk=article_id).update(views=models.F('views')+1)

def get_articles_by_tag(*tags):
    """Get Articles by tags

        Retrieves queryset of all Articles containing specified tag(s).

    Parameters:
        tags: str[] tags 
    Returns
        queryset of matched Articles
    """
    return Article.objects.filter(tags__title__in=tags)

def search(query):
    """Retrieves queryset of articles whose contents contains specified querystring.

    Parameters
    :param: str query - query string to search for

    Returns 
    :queryset: Article
    """
    return Article.objects.filter(contents__icontains=query)
