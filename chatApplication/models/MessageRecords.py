from django.conf import settings
from django.db import models

from chatApplication.models.Users import User


class MessageRecord(models.Model):

    date_sent = models.DateTimeField('Date Sent', db_index=True, unique=False)
    message = models.CharField(max_length=settings.MAX_MESSAGE_LENGTH)
    sender = models.ForeignKey(User, to_field='username', db_column='sender_username',
                               related_name='sender',
                               on_delete=models.RESTRICT)

    receiver = models.ForeignKey(User, to_field='username', db_column='receiver_username',
                                 related_name='receiver',
                                 on_delete=models.RESTRICT)

    def save(self, *args, **kwargs):
        # Clear datetime of microseconds before save
        self.date_sent = self.date_sent.replace(microsecond=0)
        super(MessageRecord, self).save(*args, **kwargs)

    def __repr__(self):
        return f'Date: {self.date_sent}: receiver - {self.receiver} | Sender: {self.sender}'

    def __str__(self):
        return f'Date: {self.date_sent}: receiver - {self.receiver} | Sender: {self.sender}'
