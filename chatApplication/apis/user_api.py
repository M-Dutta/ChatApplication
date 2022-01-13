from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET

from chatApplication.errors.api_errors import APIError
from chatApplication.errors.decorators import api_exception_handler
from chatApplication.models.Users import User


@require_POST
@api_exception_handler
def create_user(request, username):
    user, created = User.objects.api_get_or_create(username=username)
    return JsonResponse(dict(id=user.id, username=user.username), status=201 if created else 200)


@require_GET
@api_exception_handler
def get_user(request, username):
    try:
        user = User.objects.get(username=username)
        return JsonResponse(dict(id=user.id, username=username))
    except User.DoesNotExist:
        raise APIError(message='User does not exist', status=404)


@require_GET
@api_exception_handler
def all_users(request):
    users = list(User.objects.all().values('id', 'username'))
    return JsonResponse(users, safe=False)
