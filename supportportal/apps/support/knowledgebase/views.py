# System
import logging
from django.shortcuts import render, get_object_or_404
# Project
from apps.loggers.models import ActionLogger
from common.decorators import validated_request, validated_staff
from common.helpers import format_ajax_response
# App
from .models import Article, Tag, Category, increment_articles_views
from .forms import CategoryForm, TagForm, ArticleForm


logger = logging.getLogger(__name__)


def index(request, category_id=0, tag_id=0):
    """Knowledgebase Index View

        Lists categories and popular/recently modified articles.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        None
    Parameters
        request: HttpRequest
        *category_id: int category id
        *tag_id: int tag id
    Returns
        HttpReponse (knowledgebase/index.html)
    """
    response = {}

    if int(category_id):
        category = get_object_or_404(Category, pk=category_id)
        response.update({
            'category_id': category_id,
            'category': category.title
        })
    elif int(tag_id):
        tag = get_object_or_404(Tag, pk=tag_id)
        response.update({
            'tag_id': tag_id,
            'tag': tag.title
        })

    return render(request, 'knowledgebase/index.html', response)


def detail(request, article_id):
    """Knowledgebase Detail View

        Retrieves specified article's details.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        None
    Parameters
        request: HttpRequest
        article_id: int article id
    Returns
        HttpResponse (knowledgebase/detail.html)
            article_id: int article id
    """
    return render(request, 'knowledgebase/detail.html', {'article_id': article_id})


@validated_staff
def admin(request):
    """Knowledgebase Admin View

        Lists categories and popular/recently modified articles.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        None
    Parameters
        request: HttpRequest
    Returns
        HttpReponse (knowledgebase/admin.html)
            articleForm: modelform ArticleForm
            categoryform: modelform CategoryForm
            tagform: modelform TagForm
    """
    response = {
        'articleform': ArticleForm(),
        'categoryform': CategoryForm(),
        'tagform': TagForm()
    }

    return render(request, 'knowledgebase/admin.html', response)


@validated_request(None)
def get_articles(request):
    """Get Articles

        Lists articles under optional category/tag.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
            *category_id: int category id
            *tag_id: int tag id
    Returns
        HttpResponse (JSON)
            success: int status result
            message: str response message
            *data:
                articles:
    """
    try:
        if 'category_id' in request.POST and int(request.POST['category_id']):
            queryset = Article.objects.filter(category_id=int(request.POST['category_id']))
        elif 'tag_id' in request.POST and int(request.POST['tag_id']):
            queryset = Article.objects.filter(tags__pk=request.POST['tag_id'])
        else:
            queryset = Article.objects.all()

        articles = []
        for article in queryset:
            articles.append(article.dump_to_dict())

        return format_ajax_response(True, "Knowledgebase articles listing retrieving successfully.", {"articles": articles})
    except Exception as ex:
        logger.error("Failed to get_articles: %s" % ex)
        return format_ajax_response(False, "There was an error retrieving knowledgebase articles listing.")


@validated_request(None)
def get_featured_articles(request):
    """Get Featured Articles

        Lists most popular and newest articles.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
        *count: int featured articles length
    Returns
        HttpResponse (JSON)
            success: int status result
            message: str response message
            *data:
                newest: dict of newest article(s)
                popular: dict of most viewed article(s)
    """
    try:
        count = 1
        if 'count' in request.POST and int(request.POST['count']):
            count = int(request.POST['count'])

        newest_list = []
        for article in Article.objects.order_by('-modified')[:count]:
            newest_list.append(article.dump_to_dict())

        popular_list = []
        for article in Article.objects.order_by('-views')[:count]:
            popular_list.append(article.dump_to_dict())

        return format_ajax_response(True, "Featured articles retrieved successfully.", {'newest': newest_list,'popular': popular_list})
    except Exception as ex:
        logger.error("Failed to get_featured_articles: %s" % ex)
        return format_ajax_response(False, "There was an error retrieving the featured articles.")


@validated_request(None)
def get_article(request, article_id):
    """Get Article

        Retrieves specified Article.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
        article_id: int article id
    Returns
        HttpResponse (JSON)
            success: int status result
            message: str response message
            *data:
                article:
                    id: int article id
                    author: str article's author name
                    title: str article title
                    views: int article view count
                    category: str article's category title
                    created: str article creation date
                    modified: str article last modified date
                    contents: str article contents
                    tags: dict (id,title) of article tags
    """
    try:
        article = Article.objects.get(pk=article_id)
        increment_articles_views(article_id)
        return format_ajax_response(True, "Knowledgebase article retrieved successfully.", {"article": article.dump_to_dict()})
    except Exception as ex:
        logger.error("Failed to get_article: %s" % ex)
        return format_ajax_response(False, "There was an error retrieving the knowledgebase article.")


@validated_staff
@validated_request(ArticleForm)
def set_article(request):
    """Set Article

        Creates new or updates existing Article.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_staff
            request.user.is_staff must be True
        @validated_request
            request.POST must validate against ArticleForm
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
            contents: str article contents
            title: str article title
            category: int category id
            *tags: int[] tag id's
            *article_id: int article id
    Returns
        HttpResponse (JSON)
            success: int status result
            message: str response message
    """
    try:
        # Update existing Article if article_id exists, else create new Article
        if "article_id" not in request.POST or not int(request.POST["article_id"]):
            # Create new Article
            article = Article.objects.create(category=request.form.cleaned_data["category"], contents=request.form.cleaned_data["contents"], title=request.form.cleaned_data["title"], author=request.user)

            tags = request.POST.getlist('tags', 0)
            if tags:
                article.tags.add(*tags)
                article.save()

            ActionLogger().log(request.user, "created", "Knowledgebase Article %s" % article)
            return format_ajax_response(True, "Knowledgebase article created successfully.", {"article_id": article.pk})
        else:
            # Update existing category
            article = Article.objects.get(pk=int(request.POST["article_id"]))
            article.views = request.form.cleaned_data["views"]
            article.title = request.form.cleaned_data["title"]
            article.contents = request.form.cleaned_data["contents"]
            article.category = request.form.cleaned_data["category"]

            article.tags.clear()
            tags = request.POST.getlist('tags', 0)
            if tags:
                article.tags.add(*tags)
            article.save()

            ActionLogger().log(request.user, "modified", "Knowledgebase Article %s" % article)
            return format_ajax_response(True, "Knowledgebase article updated successfully.", {"article_id": article.pk})
    except Exception as ex:
        logger.error("Failed to set_article: %s" % ex)
        return format_ajax_response(False, "There was an error setting the knowledgebase article.")


@validated_staff
@validated_request(None)
def delete_article(request):
    """Delete Article

        Deletes the specified Article.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_staff
            request.user.is_staff must be True
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
            article_id: int article id
    Returns
        HttpResponse (JSON)
            success: int status result
            message: str response message
    """
    try:
        articles = request.POST.getlist('article_id')
        Article.objects.filter(pk__in=articles).delete()
        ActionLogger().log(request.user, "deleted", "Knowledgebase Article %s" % articles)
        return format_ajax_response(True, "Knowledgebase article(s) deleted successfully.")
    except Exception as ex:
        logger.error("Failed to delete_article: %s" % ex)
        return format_ajax_response(False, 'There was an error deleting the knowledgebase article(s).')


@validated_staff
@validated_request(TagForm)
def set_tag(request):
    """Creates/Updates Knowledgebase Tag

        Updates the title of an existing Knowledgebase Tag or
        Creates a new Knowledgebase Tag if no PK supplied.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_staff
            request.user.is_staff must be True
        @validated_request
            request.POST must validate against TagForm
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
            title: str tag title
            *tag_id: int tag id
    Returns
        HttpResponse (JSON)
            success: int status result
            message: str response message
    """
    try:
        # Update existing Tag if tag_id exists, else create new Tag
        if "tag_id" not in request.POST or not request.POST["tag_id"]:
            # Create new Tag
            tag = Tag.objects.create(title=request.form.cleaned_data["title"])

            ActionLogger().log(request.user, "created", "Knowledgebase Tag %s" % tag)
            return format_ajax_response(True, "Knowledgebase tag created successfully.")
        else:
            # Update existing category
            tag = Tag.objects.get(pk=request.POST["tag_id"])
            tag.title = request.form.cleaned_data["title"]
            tag.save()

            ActionLogger().log(request.user, "modified", "Knowledgebase Tag %s" % tag)
            return format_ajax_response(True, "Knowledgebase tag updated successfully.")
    except Exception as ex:
        logger.error("Failed to set_tag: %s" % ex)
        return format_ajax_response(False, "There was an error setting the specified knowledgebase tag.")


@validated_staff
@validated_request(None)
def delete_tag(request):
    """Delete Tag

        Deletes specified Tag.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_staff
            request.user.is_staff must be True
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
            tag_id: int[] article id
    Returns
        HttpResponse (JSON)
            success: int status result
            message: str response message
    """
    try:
        tags = request.POST.getlist('tag_id', 0)
        tag = Tag.objects.filter(pk__in=tags).delete()
        ActionLogger().log(request.user, "deleted", "Knowledgebase Tag %s" % tags)
        return format_ajax_response(True, "Knoweldgebase tag deleted successfully.")
    except Exception as ex:
        logger.error("Failed to delete_tag: %s" % ex)
        return format_ajax_response(False, "There was an error deleting the specified knowledgebase tag.")


@validated_staff
@validated_request(None)
def get_tags(request):
    """Get Tags

        Lists Tags.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_staff
            request.user.is_staff must be True
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
    Returns
        HttpResponse (JSON)
            success: int status result
            message: str response message
            *data:
                tags:
                    title: str tag title
                    id: int tag id
    """
    try:
        tags = []
        for tag in Tag.objects.all():
            tags.append({"title": tag.title, "id": tag.pk})

        return format_ajax_response(True, "Knowledgebase tags retrieved successfully.", {"tags": tags})
    except Exception as ex:
        logger.error("Failed to get_tags: %s" % ex)
        return format_ajax_response(False, "There was an error retrieving the knowledgebase tags.")


@validated_staff
@validated_request(None)
def get_categories(request):
    """Get Categories

        Lists Categories.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_staff
            request.user.is_staff must be True
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
    Returns
        HttpResponse (JSON)
            success: int status result
            message: str response message
            *data:
                categories:
                    title: str category name
                    id: int category id
    """
    try:
        categories = []
        for category in Category.objects.all():
            categories.append({"title": category.title, "id": category.pk})

        return format_ajax_response(True, "Knowledgebase categories retrieved successfully.", {"categories": categories})
    except Exception as ex:
        logger.error("Failed to get_categories: %s" % ex)
        return format_ajax_response(False, "There was an error retreiving the knowledgebase categories.")


@validated_staff
@validated_request(None)
def delete_category(request):
    """Delete Category

        Deletes Category.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_staff
            request.user.is_staff must be True
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
            category_id: int category id
    Returns
        HttpResponse (JSON)
            success: int status result
            message: str response message
    """
    try:
        categories = request.POST.getlist('category_id', 0)
        category = Category.objects.filter(pk__in=categories).delete()
        ActionLogger().log(request.user, "deleted", "Knowledgebase Category %s" % categories)
        return format_ajax_response(True, "Knowledgebase category(s) deleted successfully.")
    except Exception as ex:
        logger.error("Failed to delete_category: %s" % ex)
        return format_ajax_response(False, "There was an error deleting knowledgebase category(s).")


@validated_staff
@validated_request(CategoryForm)
def set_category(request):
    """Set Category

        Creates new or updates existing Category.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_staff
            request.user.is_staff must be True
        @validated_request
            request.POST must validate against CategoryForm
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
            title: str category title
            *category_id: int category id
    Returns
        HttpResponse (JSON)
            success: int status result
            message: str response message
    """
    try:
        # Update existing category if category_id exists, else create new Category
        if "category_id" not in request.POST or not request.POST["category_id"]:
            # Create new Category
            category = Category.objects.create(title=request.form.cleaned_data["title"])

            ActionLogger().log(request.user, "created", "Knowledgebase Category %s" % category)
            return format_ajax_response(True, "Knowledgebase category created successfully.")
        else:
            # Update existing category
            category = Category.objects.get(pk=request.POST["category_id"])
            category.title = request.form.cleaned_data["title"]
            category.save()

            ActionLogger().log(request.user, "modified", "Knowledgebase Category %s" % category)
            return format_ajax_response(True, "Knowledgebase category updated successfully.")
    except Exception as ex:
        logger.error("Failed to set_category: %s" % ex)
        return format_ajax_response(False, "There was an error setting the knowledgebase category.")