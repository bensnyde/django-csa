# System
import logging
# Project
from apps.loggers.models import ActionLogger
from common.decorators import validated_request, validated_staff
from common.helpers import format_ajax_response
# App
from .models import Announcement
from .forms import AnnouncementForm


logger = logging.getLogger(__name__)


@validated_request(None)
def get_news(request):
    """Get News postings

        Retrieves the most recent news postings from the local database.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True        
    Paremeters
        request: HttpRequest
    Returns
        HttpResponse (JSON)
            success: int status result 
            message: str response message 
            *data: 
                news: 
                    title: str title of news posting
                    body: str contents of news posting
                    timestamp: str short formatted time of posting
                    author: str posting's author's name
    """
    try:
        if request.user.is_staff:
            qset = Announcement.objects.order_by('-timestamp')[:5]
        else:
            qset = Announcement.objects.filter(public=True).order_by('-timestamp')[:5]

        news = []
        for post in qset:
            news.append(post.dump_to_dict())

        return format_ajax_response(True, "News retrieved successfully.", {"news": news})
    except Exception as ex:
        logger.error("Failed to get_news: %s" % ex)
        return format_ajax_response(False, "There was a problem retrieving News postings.")
  

@validated_staff
@validated_request(AnnouncementForm)
def set_news(request):
    """Set a News posting

        Creates a News posting in the local database.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_staff
            request.user.is_staff must be True    
        @validated_request
            request.POST must validate against AnnouncementForm       
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True         
    Paremeters
        request: HttpRequest
    Returns
        HttpResponse (JSON)
            success: int status result 
            message: str response message 
    """
    try:
        if "news_id" not in request.POST or request.POST["news_id"] is not 0:
            # Create new
            post = Announcement.objects.create(title=request.form.cleaned_data["title"], body=request.form.cleaned_data["body"], author=request.user)
            ActionLogger().log(request.user, "created", "News posting %s" % post)
            return format_ajax_response(True, "News article created successfully.")
        else:
            # Update existing
            post = Announcement.objects.get(pk=int(request.POST["news_id"]))
            post.title = request.form.cleaned_data["title"]
            post.body = request.form.cleaned_body["body"]
            post.author = request.user
            post.save()

            ActionLogger().log(request.user, "modified", "News Article %s" % post)
            return format_ajax_responsee(True, "News Article updated successfully.")
    except Exception as ex:
        logger.error("Failed to set_news: %s" % ex)
        return format_ajax_response(False, "There was a problem setting the specified article.")


@validated_staff
@validated_request(None)
def delete_news(request):
    """Delete News posting

        Deletes News posting(s) from the local database.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_staff
            request.user.is_staff must be True     
        @validated_request
            request.POST must validate against AnnouncementForm        
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True         
    Paremeters
        request: HttpRequest
    Returns
        HttpResponse (JSON)
            success: int status result 
            message: str response message 
    """
    try:
        posts = request.POST.getlist('news_id[]')
        Announcement.objects.filter(pk__in=posts).delete()
        ActionLogger().log(request.user, "deleted", "News Article(s) %s" % posts)
        return format_ajax_responsee(True, "News Article(s) deleted successfully.")
    except Exception as ex:
        logger.error("Failed to delete delete_news: %s" % ex)
        return format_ajax_response(False, "There was a problem deleting the specified article(s).")
