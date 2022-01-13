import json
import logging
from datetime import datetime, timedelta
from json import JSONDecodeError
from typing import Union, List
from urllib.parse import parse_qsl

import pytz
from django.conf import settings
from django.core.handlers.asgi import ASGIRequest
from django.core.paginator import Paginator
from django.db.models import QuerySet
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET

from chatApplication.errors.api_errors import APIError
from chatApplication.errors.decorators import api_exception_handler
from chatApplication.models import MessageRecord
from chatApplication.models.Users import User


def content_extractor(request):
    try:
        content = json.loads(request.body)
        sender = str(content['sender'])
        message = str(content['message'])
        if len(message) > settings.MAX_MESSAGE_LENGTH:
            raise APIError(f'Max message length({settings.MAX_MESSAGE_LENGTH}) exceeded')

        return sender, message
    except KeyError:
        raise APIError(message="message is required; sender is required")
    except JSONDecodeError:
        raise APIError(message="Content-Type must be application/json")


@require_POST
@api_exception_handler
def send_message(request: ASGIRequest, receiver_username: str, date_time_sent_utc=datetime.now(pytz.UTC)):
    sender_username, message = content_extractor(request)
    sender = User.objects.api_get(username=sender_username)
    receiver = User.objects.api_get(username=receiver_username)

    record = MessageRecord(sender=sender,
                           receiver=receiver,
                           message=message,
                           date_sent=date_time_sent_utc
                           )
    record.save()
    logging.debug(f'{date_time_sent_utc}:\nSent by: {sender}\nSent to {receiver}\n{message}')
    return JsonResponse(dict(status='success', date_sent=date_time_sent_utc.isoformat()))


@require_GET
@api_exception_handler
def retrieve_messages(request: ASGIRequest):
    """
    Retrieves Messages sent to the the request user by the sender_id
    Range is handled in this entry function
    Pagination is handled in the base_retriever
    utc_today_max: 1 second before tomorrow
    """

    try:
        content = dict(parse_qsl(request.body.decode('utf8').strip()))
        sender_username = str(content['sender'])
        receiver_username = str(content['receiver'])
    except (KeyError, ValueError) as e:
        raise APIError(["sender is required and must be a username string",
                        "receiver is required and must be a username string",
                        "Content-Type must be application/x-www-form-urlencoded"])

    records = MessageRecord.objects.values('date_sent', 'message').filter(
        date_sent__range=create_filter_range(),
        sender__username=sender_username,
        receiver__username=receiver_username
    ).order_by('-date_sent')
    return base_retriever(record_queryset=records,
                          page=request.GET.get('page', 1),
                          per_page=request.GET.get('per_page', settings.DEFAULT_MAX_DATA_PER_PAGE)
                          )


@require_GET
@api_exception_handler
def retrieve_all_messages(request: ASGIRequest):
    """
    All Senders
    Range is handled in this entry function
    Pagination is handled in the base_retriever
    """

    records = MessageRecord.objects.values('sender', 'date_sent', 'message', 'receiver'
                                           ).filter(date_sent__range=create_filter_range()
                                                    ).order_by('-date_sent')

    return base_retriever(record_queryset=records,
                          page=request.GET.get('page', 1),
                          per_page=request.GET.get('per_page', settings.DEFAULT_MAX_DATA_PER_PAGE)
                          )


def base_retriever(record_queryset: QuerySet, page: Union[int, str], per_page: Union[int, str]):
    # Default records
    try:
        page = int(page)
        per_page = int(per_page)
        per_page = settings.DEFAULT_MAX_DATA_PER_PAGE if per_page > settings.DEFAULT_MAX_DATA_PER_PAGE else per_page
    except ValueError:
        raise APIError(["query param page must be int", "query param per_page must be int"])

    paginated_records = Paginator(record_queryset, per_page=per_page)

    # Get the page requested. Validate that it's within paginated record-book bound
    if int(page) >= paginated_records.page_range.stop:
        return JsonResponse({}, safe=False)

    # Prep response and return
    page_records = []  # Collect formatted data here
    for obj in paginated_records.page(page).object_list:
        obj['date_sent'] = obj['date_sent'].isoformat()
        page_records.append(obj)
    return JsonResponse(page_records, safe=False)


def utc_today_max() -> datetime:
    return datetime.now(pytz.UTC).replace(hour=23, minute=59, second=59, microsecond=999999)


def create_filter_range(date_range=settings.DEFAULT_DATE_RANGE) -> List[datetime]:
    """
    latest date = max of today,
    earliest date = start of latest date - range
    :return:
    """
    end = datetime.now(tz=pytz.UTC)
    start = (end - timedelta(date_range)).replace(hour=0, minute=0, second=0, microsecond=0)
    return [start, end]
