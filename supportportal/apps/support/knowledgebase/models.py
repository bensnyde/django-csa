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
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, blank=False)
    title = models.CharField(max_length=128, blank=False, null=False)
    contents = models.TextField(blank=False, null=False)
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()
    views = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, blank=False, null=False)
    tags = models.ManyToManyField(Tag, blank=True, null=True)

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
            "category_id": self.category.pk,
        	"created": defaultfilters.date(self.created, "SHORT_DATETIME_FORMAT"),
        	"modified": defaultfilters.date(self.modified, "SHORT_DATETIME_FORMAT"),
        	"contents": self.contents,
        	"tags": tags
        }


def get_article_count(author_id=0, startdate=0, enddate=0):
    try:
        filters = dict()

        if author_id:
            filters.update({"author_id": author_id})

        if startdate and enddate:
            filters.update({"created__range": [startdate, enddate]})
        elif startdate:
            filters.update({"created__gt": startdate})

        return Article.objects.filter(**filters).count()
    except Exception as ex:
        return False


def increment_articles_views(article_id):
    """Increment Article views

        Increments view count on specified Article.

    Parameters
        article_id: int article id
    Returns
        bool result
    """
    try:
        Article.objects.filter(pk=article_id).update(views=models.F('views')+1)
        return True
    except Exception as ex:
        return False


def search(query):
    """Retrieves queryset of articles whose contents contains specified querystring.

    Parameters
    :param: str query - query string to search for

    Returns
    :queryset: Article
    """
    try:
        return Article.objects.filter(contents__icontains=query)
    except Exception as ex:
        return False