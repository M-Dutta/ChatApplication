import json
from datetime import datetime, timedelta

import pytz
from django.conf import settings
from django.test import TestCase, Client

from chatApplication.constants import DEFAULT_DATE_RANGE
from chatApplication.models import MessageRecord
from chatApplication.models.Users import User


class SendAPITest(TestCase):
    def setUp(self):
        self.sender = User.objects.create(username='sender')
        self.receiver = User.objects.create(username='receiver')
        self.client = Client()

    def test_api_send_message_valid(self):
        self.assertIsNotNone(self.sender.id)
        self.assertIsNotNone(self.receiver.id)
        message = "Test Message"
        response = self.client.post(f'/message/send/{self.receiver.username}',
                                    data=dict(sender=self.sender.username, message=message),
                                    content_type='application/json',
                                    )
        self.assertTrue(response.status_code == 200)
        self.assertIsNotNone(MessageRecord.objects.filter(sender=self.sender,
                                                          receiver=self.receiver,
                                                          message=message).first()
                             )

    def test_send_message_bad_content(self):
        response = self.client.post(f'/message/send/{self.receiver.username}',
                                    data=dict(),
                                    content_type='application/json',
                                    )
        self.assertTrue(response.status_code, 400)

    def test_sender_doesnt_exist(self):
        message = "Test Message"
        non_existent_username = 'non-existent'
        self.assertIsNone(User.objects.filter(username=non_existent_username).first())
        response = self.client.post(f'/message/send/{self.receiver.username}',
                                    data=dict(sender=non_existent_username, message=message),
                                    content_type='application/json',
                                    HTTP_USER_ID=User.objects.last().id + 1
                                    )
        self.assertTrue(response.status_code == 400)

    def test_receiver_does_not_exist(self):
        message = "Test Message"
        non_existent_username = 'non-existent'
        self.assertIsNone(User.objects.filter(username=non_existent_username).first())
        response = self.client.post(f'/message/send/{non_existent_username}',
                                    data=dict(sender=self.sender.username, message=message),
                                    content_type='application/json',
                                    )
        self.assertTrue(response.status_code == 400)


class RetrieveAPITest(TestCase):
    def setUp(self):
        self.sender = User.objects.create(username='sender')
        self.second_sender = User.objects.create(username='second_sender')
        self.receiver = User.objects.create(username='receiver')
        self.client = Client()
        self.base_endpoint = '/message/retrieve'
        self.utc_now = datetime.now(pytz.UTC).replace(microsecond=0)
        for i in range(0, 101):
            MessageRecord(date_sent=self.utc_now - timedelta(days=i),
                          message=f'sent {i} day(s) ago by user {self.sender.username}',
                          sender=self.sender,
                          receiver=self.receiver).save()

        for i in range(0, 101):
            MessageRecord(date_sent=self.utc_now - timedelta(days=i),
                          message=f'sent {i} day(s) ago by user {self.second_sender.username}',
                          sender=self.second_sender,
                          receiver=self.receiver).save()

    def _pagination_test_populator(self, sender, receiver):
        for i in range(0, settings.DEFAULT_MAX_DATA_PER_PAGE):
            MessageRecord(date_sent=self.utc_now - timedelta(hours=i),
                          message=f'sent {i} day(s) ago by user {sender.username}',
                          sender=sender,
                          receiver=receiver).save()

    def test_api_for_user_from_user_returns_valid(self):
        data = f"sender={self.sender.username}&receiver={self.receiver.username}"
        response = self.client.generic('GET',
                                       f'{self.base_endpoint}/',
                                       data=data,
                                       content_type='application/x-www-form-urlencoded')
        self.assertEqual(response.status_code, 200)

        message_list = json.loads(response.content)
        self.assertTrue(len(message_list) > 0)

        for x in message_list:
            self.assertEqual(x['message'].rsplit(' ', 1)[-1], self.sender.username)
            self.assertIsNotNone(x['date_sent'])

    def test_api_messages_from_all_user_returns_valid(self):
        response = self.client.get(f'{self.base_endpoint}/all/')
        self.assertEqual(response.status_code, 200)

        message_list = json.loads(response.content)
        self.assertTrue(len(message_list) > 0)

        self.assertEqual(response.status_code, 200)
        sender_set = {self.sender.username, self.second_sender.username}
        collector = set()
        for x in message_list:
            self.assertEqual(x['message'].rsplit(' ', 1)[-1], str(x['sender']))
            self.assertIsNotNone(x['date_sent'])
            self.assertIsNotNone(x['sender'])
            self.assertIsNotNone(x['receiver'])
            collector.add(x['sender'])
        self.assertEqual(sender_set, collector)

    def test_api_for_user_from_user_message_results_are_limited_to_default_date_limit(self):
        data = f"sender={self.sender.username}&receiver={self.receiver.username}"
        response = self.client.generic('GET',
                                       f'{self.base_endpoint}/',
                                       data=data,
                                       content_type='application/x-www-form-urlencoded')
        self.assertEqual(response.status_code, 200)

        message_list = json.loads(response.content)
        self.assertTrue(len(message_list) > 0)

        # Verify beginning is utc_now
        self.assertTrue(message_list[0]['date_sent'], self.utc_now.isoformat())
        # Verify last date is 30 days away
        self.assertTrue(message_list[-1]['date_sent'], (self.utc_now - timedelta(DEFAULT_DATE_RANGE)).isoformat())

    def test_api_for_user_from_user_message_results_are_limited_to_default_pagination_limit(self):

        self._pagination_test_populator(sender=self.sender, receiver=self.receiver)

        data = f"sender={self.sender.username}&receiver={self.receiver.username}"
        response = self.client.generic('GET',
                                       f'{self.base_endpoint}/',
                                       data=data,
                                       content_type='application/x-www-form-urlencoded')
        self.assertTrue(response.status_code, 200)

        message_list = json.loads(response.content)
        self.assertTrue(len(message_list) > 0)

        self.assertEqual(len(message_list), settings.DEFAULT_MAX_DATA_PER_PAGE)

    def test_api_messages_from_all_users_are_limited_to_default_date_range_limit(self):
        response = self.client.get(f'{self.base_endpoint}/all/')
        self.assertTrue(response.status_code, 200)

        message_list = json.loads(response.content)
        self.assertTrue(len(message_list) > 0)
        # Verify beginning is utc_now
        self.assertTrue(message_list[0]['date_sent'], self.utc_now.isoformat())
        # Verify last date is 30 days away
        self.assertTrue(message_list[-1]['date_sent'], (self.utc_now - timedelta(DEFAULT_DATE_RANGE)).isoformat())

    def test_api_messages_from_all_users_are_limited_to_default_pagination_limit(self):
        self._pagination_test_populator(sender=self.second_sender, receiver=self.receiver)
        response = self.client.get(f'{self.base_endpoint}/all/')
        self.assertEqual(response.status_code, 200)
        message_list = json.loads(response.content)
        self.assertEqual(len(message_list), settings.DEFAULT_MAX_DATA_PER_PAGE)

    def test_api_messages_respect_query_params(self):
        per_page = 10
        data = f"sender={self.sender.username}&receiver={self.receiver.username}"
        response = self.client.generic('GET',
                                       f'{self.base_endpoint}/?per_page={per_page}',
                                       data=data,
                                       content_type='application/x-www-form-urlencoded')
        self.assertEqual(response.status_code, 200)
        message_list = json.loads(response.content)
        self.assertEqual(len(message_list), per_page)
        self.assertEqual(self.utc_now.isoformat(), message_list[0]['date_sent'])
        self.assertEqual((self.utc_now - timedelta(per_page - 1)).isoformat(), message_list[-1]['date_sent'])

        # page 2
        response = self.client.generic('GET',
                                       f'{self.base_endpoint}/?per_page={per_page}&page=2',
                                       data=data,
                                       content_type='application/x-www-form-urlencoded')
        self.assertEqual(response.status_code, 200)
        message_list = json.loads(response.content)
        self.assertEqual(len(message_list), per_page)
        self.assertEqual((self.utc_now - timedelta(per_page)).isoformat(), message_list[0]['date_sent'])
        self.assertEqual((self.utc_now - timedelta(per_page*2 - 1)).isoformat(), message_list[-1]['date_sent'])

    def test_api_non_existent_users_return_empty_result(self):
        non_existent_username = 'non-existent'
        self.assertIsNone(User.objects.filter(username=non_existent_username).first())

        data = f"sender={non_existent_username}&receiver={self.receiver.username}"
        response = self.client.generic('GET',
                                       f'{self.base_endpoint}/',
                                       data=data,
                                       content_type='application/x-www-form-urlencoded')
        self.assertTrue(response.status_code, 200)

        message_list = json.loads(response.content)
        self.assertEqual(len(message_list), 0)
