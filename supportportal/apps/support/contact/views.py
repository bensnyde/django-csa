from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def index(request):
    """Contact Base View

        Displays contact information and form.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @login_required
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
    Returns
        HttpResponse (contact/index.html)
            contact_form: Form contact form
    """
    return render(request, 'contact/index.html')