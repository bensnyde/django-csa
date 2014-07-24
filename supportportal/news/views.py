from apps.loggers.models import ErrorLogger, ActionLogger
from common.decorators import validated_request, validated_staff
from news.models import News
from news.forms import NewsForm


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
            data: 
                news: 
                    title: str title of news posting
                    body: str contents of news posting
                    timestamp: str short formatted time of posting
                    author: str posting's author's name
    """
    try:
        news = []
        for post in News.objects.order_by('-timestamp')[:5]:
            news.append(post.dump_to_dict())

        return {
            'success': 1,
            'message': 'News retrieved successfully.',
            'data': {
                'news': news
            }
        }
    except Exception as ex:
        ErrorLogger().log(request, "Failed", "Failed to retrieve News in news.get_news: %s" % ex)
        return {
            'success': 0,
            'message': "There was a problem retrieving News postings."
        }
  

@validated_staff
@validated_request(NewsForm)
def set_news(request):
    """Set a News posting

        Creates a News posting in the local database.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_staff
            request.user.is_staff must be True    
        @validated_request
            request.POST must validate against NewsForm       
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
        # Update existing if news_id exists, else create new
        if "news_id" not in request.POST or request.POST["news_id"] is not 0:
            # Create
            post = News.objects.create(title=request.form.cleaned_data["title"], body=request.form.cleaned_data["body"], author=request.user)

            ActionLogger().log(request.user, "created", "News posting %s" % post)
            message = "News article created successfully."
        else:
            # Update existing
            post = get_object_or_404(News, pk=int(request.POST["news_id"]))
            post.title = request.form.cleaned_data["title"]
            post.body = request.form.cleaned_body["body"]
            post.author = request.user
            post.save()

            ActionLogger().log(request.user, "modified", "News Article %s" % post)
            message = "News Article updated successfully."

        return {
            'success': 1,
            'message': message,
        }
    except Exception as ex:
        ErrorLogger().log(request, "Failed", "Failed to set News in news.set_news: %s" % ex)
        return {
            'success': 0,
            'message': "There was a problem setting the specified article."
        }


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
            request.POST must validate against NewsForm        
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
        News.objects.filter(pk__in=posts).delete()
        ActionLogger().log(request.user, "deleted", "News Article(s) %s" % posts)
        return {
            'success': 1,
            'message': "News Article(s) deleted successfully.",
        }
    except Exception as ex:
        ErrorLogger().log(request, "Failed", "Failed to delete Article(s) in news.delete_news: %s" % ex)
        return {
            'success': 0,
            'message': "There was a problem deleting the specified article(s)."
        }