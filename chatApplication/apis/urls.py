from django.urls import path

from chatApplication.apis.message_api import send_message, retrieve_messages, retrieve_all_messages
from chatApplication.apis.user_api import create_user, get_user, all_users

urlpatterns = [
    path('message/send/<str:receiver_username>', send_message, name='send'),  # Send Message
    path('message/retrieve/', retrieve_messages, name='retrieve'),  # Specific sender
    path('message/retrieve/all/', retrieve_all_messages, name='retrieve-all'),  # all senders

    path('user/create-user/<str:username>', create_user, name='create-user'),
    path('user/get-user/<str:username>', get_user, name='get-user'),
    path('user/all-users/', all_users, name='get-user')
]
