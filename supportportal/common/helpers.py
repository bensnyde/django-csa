from django.http import HttpResponse
import json
import logging

logger = logging.getLogger(__name__)

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
    try:
        response = {
            "success": success,
            "message": message
        }

        if data:
            response.update({"data": data})

        if errors:
            response.update({"errors": errors})

        response = json.dumps(response)
    except Exception as ex:
        logger.error('Failed to json encode response string: %s' % ex)
        response = False

    return HttpResponse(response, 'application/json')