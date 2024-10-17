from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Customize the response here
        response.data = {
            'error': True,
            'message': response.data
        }
    else:
        # For unhandled exceptions, return a generic message
        return Response(
            {'error': True, 'message': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response
