from django.http import HttpResponse
import json

def format_ajax_response(success, message, data=False, errors=False):
    """Format standard AJAX response

        Formats and encodes standard JSON response for AJAX queries.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        None
    Parameters
        success: bool response status
        message: str response status message
        *data: dict data to be included in response
        *errors: dict form errors
    Returns
        Response (JSON)
            success: bool response status
            message: str response status message
            *data: dict additional data
    """        
    response = {
        "success": success,
        "message": message
    }

    if data:
        response.update({"data": data})

    if errors:
        response.update({"errors": errors})

    return HttpResponse(json.dumps(response), 'application/json')