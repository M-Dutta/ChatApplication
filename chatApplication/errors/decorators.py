import functools

from django.http import JsonResponse

from chatApplication.errors.api_errors import APIError


def api_exception_handler(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except APIError as e:
            return JsonResponse(dict(error=e.message), status=e.status)

    return inner
