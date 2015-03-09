from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from .models import Article, Tag, Category
from .forms import CategoryForm, TagForm, ArticleForm


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


@staff_member_required
def admin(request):
    """Knowledgebase Admin View

        Lists categories and popular/recently modified articles.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        staff_member_required
    Parameters
        request: HttpRequest
    Returns
        HttpReponse (knowledgebase/admin.html)
            articleform: modelform ArticleForm
            categoryform: modelform CategoryForm
            tagform: modelform TagForm
    """
    response = {
        'articleform': ArticleForm(),
        'categoryform': CategoryForm(),
        'tagform': TagForm()
    }

    return render(request, 'knowledgebase/admin.html', response)