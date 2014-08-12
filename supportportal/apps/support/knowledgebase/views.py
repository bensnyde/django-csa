# System
import logging
from django.shortcuts import render
# Project
from apps.loggers.models import ActionLogger
from common.decorators import validated_request, validated_staff
from common.helpers import format_ajax_response
# App
from .models import Article, Tag, Category, get_categories_annotate_articles, increment_articles_views
from .forms import CategoryForm, TagForm, ArticleForm


logger = logging.getLogger(__name__)


def index(request):
    """Knowledgebase Index View

        Lists categories and popular/recently modified articles. 

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        None   
    Parameters
        request: HttpRequest
    Returns
        HttpReponse (knowledgebase/index.html)
    """
    return render(request, 'knowledgebase/index.html')


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
def admin(request, article_id=0):
    """Knowledgebase Index View

        Lists categories and popular/recently modified articles. 

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        None   
    Parameters
        request: HttpRequest
    Returns
        HttpReponse (knowledgebase/admin.html)
    """
    return render(request, 'knowledgebase/admin.html', {'article_id': article_id})


@validated_request(None)
def get_summary(request):
    """Get Knowledgebase Summary

        Retrieves a summary of knowledgebase categories and their respective articles.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
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
                newest: dict of newest article(s)
                popular: dict of most viewed article(s)
                categories: dict of categories annotated with respective articles
    """    
    try:
        # Fetch most recent article(s)
        newest_list = []
        for article in Article.objects.order_by('-modified')[:1]:
            newest_list.append(article.dump_to_dict())

        # Fetch most popular article(s)
        popular_list = []
        for article in Article.objects.order_by('-views')[:1]:
            popular_list.append(article.dump_to_dict())

        # Fetch entire knowledgebase overview
        kb_categories = get_categories_annotate_articles()

        return format_ajax_response(True, "Knowledgebase overview retrieved successfully.", {'newest': newest_list,'popular': popular_list,'categories': kb_categories})
    except Exception as ex:
        logger.error("Failed to get_summary: %s" % ex)
        return format_ajax_response(False, "There was an error retrieving the knowledgebase overview.")
  

@validated_request(None)
def get_article(request, article_id):
    """Get Knowledgebase Article

        Retrieves specified Knowledgebase Article.

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
    """Create/Update Knowledgebase Article

        Updates existing Knowledgebase Article or creates new a new Article if no PK is supplied.

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
    """Delete Knowledgebase Article

        Deletes the specified Knowledgebase Article.

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
        if "tag_id" not in request.POST or not int(request.POST["tag_id"]):
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
    """Delete Knowledgebase Tag(s)

        Deletes specified Tag(s) from Knowledgebase.

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
        tags = request.POST.getlist('tag_id')
        tag = Tag.objects.filter(pk__in=tags).delete()
        ActionLogger().log(request.user, "deleted", "Knowledgebase Tag(s) %s" % tags)
        return format_ajax_response(True, "Knoweldgebase tag(s) deleted successfully.")
    except Exception as ex:
        logger.error("Failed to delete_tag: %s" % ex)
        return format_ajax_response(False, "There was an error deleting the specified knowledgebase tag(s).")     


@validated_staff
@validated_request(None)
def get_tags(request):
    """Get Knowledgebase Tags

        Retrieves listing of all Tags defined in Knowledgebase.

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
    """Get Knowledgebase Categories

        Retrieves listing of all Categories defined in Knowledgebase.

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
    """Delete Knowledgebase Category

        Deletes the specified Knowledgebase Category.

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
        categories = request.POST.getlist('category_id')
        category = Category.objects.filter(pk__in=categories).delete()
        ActionLogger().log(request.user, "deleted", "Knowledgebase Category %s" % categories)
        return format_ajax_response(True, "Knowledgebase category(s) deleted successfully.")
    except Exception as ex:
        logger.error("Failed to delete_category: %s" % ex)
        return format_ajax_response(False, "There was an error deleting knowledgebase category(s).")


@validated_staff
@validated_request(CategoryForm)
def set_category(request):
    """Create/Update Knowledgebase Category

        Updates the title of an existing Knowledgebase Category or
        Creates a new Knowledgebase Category if no PK supplied.

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
        if "category_id" not in request.POST or not int(request.POST["category_id"]):
            # Create new Category
            category = Category.objects.create(title=request.form.cleaned_data["title"]) 

            ActionLogger().log(request.user, "created", "Knowledgebase Category %s" % category)
            return format_ajax_response(True, "Knowledgebase category created successfully.")
        else:
            # Update existing category
            category = Category.objects.get(pk=int(request.POST["category_id"]))
            category.title = request.form.cleaned_data["title"]
            category.save()

            ActionLogger().log(request.user, "modified", "Knowledgebase Category %s" % category)
            return format_ajax_response(True, "Knowledgebase category updated successfully.")
    except Exception as ex:
        logger.error("Failed to set_category: %s" % ex)
        return format_ajax_response(False, "There was an error setting the knowledgebase category.")