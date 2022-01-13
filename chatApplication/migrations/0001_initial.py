# Generated by Django 3.2.11 on 2022-01-13 04:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(db_index=True, max_length=16, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='MessageRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_sent', models.DateTimeField(db_index=True, verbose_name='Date Sent')),
                ('message', models.CharField(max_length=200)),
                ('receiver', models.ForeignKey(db_column='receiver_username', on_delete=django.db.models.deletion.RESTRICT, related_name='receiver', to='chatApplication.user', to_field='username')),
                ('sender', models.ForeignKey(db_column='sender_username', on_delete=django.db.models.deletion.RESTRICT, related_name='sender', to='chatApplication.user', to_field='username')),
            ],
        ),
    ]
