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
def get_index(request):
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
@validated_request(None)
def get_detail(request):
    try:
        announcement = Announcement.objects.get(pk=int(request.POST['announcement_id']))
        return format_ajax_response(True, "Announcement retrieved successfully.", {'announcement': announcement.dump_to_dict()})
    except Exception as ex:
        logger.error("Failed to get: %s" % ex)
        return format_ajax_response(False, "There was a problem retrieving the announcement.")

@validated_staff
@validated_request(AnnouncementForm)
def set(request):
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
        if "announcement_id" not in request.POST or not request.POST["announcement_id"]:
            # Create new
            post = Announcement.objects.create(title=request.form.cleaned_data["title"], body=request.form.cleaned_data["body"], author=request.user)
            ActionLogger().log(request.user, "created", "Announcement %s" % post)
            return format_ajax_response(True, "Announcement created successfully.")
        else:
            # Update existing
            post = Announcement.objects.get(pk=int(request.POST["announcement_id"]))
            post.title = request.form.cleaned_data["title"]
            post.body = request.form.cleaned_data["body"]
            post.author = request.user
            if "public" in request.POST and request.POST['public'] == "on":
                post.public= True
            else:
                post.public=False
            post.save()

            ActionLogger().log(request.user, "modified", "Announcement %s" % post)
            return format_ajax_response(True, "Announcement updated successfully.")
    except Exception as ex:
        logger.error("Failed to set: %s" % ex)
        return format_ajax_response(False, "There was a problem setting the specified announcement.")


@validated_staff
@validated_request(None)
def delete(request):
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
        posts = request.POST.getlist('announcement_id')
        Announcement.objects.filter(pk__in=posts).delete()
        ActionLogger().log(request.user, "deleted", "News Article(s) %s" % posts)
        return format_ajax_response(True, "News Article(s) deleted successfully.")
    except Exception as ex:
        logger.error("Failed to delete_news: %s" % ex)
        return format_ajax_response(False, "There was a problem deleting the specified article(s).")