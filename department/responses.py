from rest_framework import status as http_status
from rest_framework.response import Response


class SuccessResponse(Response):
    def __init__(self, data=None, message=None, status=http_status.HTTP_200_OK):
        response_data = {
            "status": "success",
            "data": data,
        }
        if message:
            response_data["message"] = message
        super().__init__(response_data, status=status)


class ErrorResponse(Response):
    def __init__(self, error, message=None, status=http_status.HTTP_400_BAD_REQUEST):
        response_data = {
            "status": "error",
            "error": error,
        }
        if message:
            response_data["message"] = message
        super().__init__(response_data, status=status)